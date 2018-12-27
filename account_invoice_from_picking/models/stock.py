# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    invoice_state = fields.Selection([
        ("invoiced", "Invoiced"),
        ("2binvoiced", "To Be Invoiced"),
        ("none", "Not Applicable")
    ], 'Invoice Control', index=True, required=True,
        track_visibility='onchange',
        states={'draft': [('readonly', False)]},
        default='none'
    )

    @api.multi
    def get_code_from_locs(
            self, move, location_id=False, location_dest_id=False):
        """
        Returns the code the picking type should have.  This can easily be used
        to check if a move is internal or not
        move, location_id and location_dest_id are browse records
        """
        code = 'internal'
        src_loc = location_id or move.location_id
        dest_loc = location_dest_id or move.location_dest_id
        if src_loc.usage == 'internal' and dest_loc.usage != 'internal':
            code = 'outgoing'
        if src_loc.usage != 'internal' and dest_loc.usage == 'internal':
            code = 'incoming'
        return code

    @api.multi
    def _get_master_data(self, move, company):
        ''' returns a tuple (browse_record(res.partner),
         ID(res.users), ID(res.currency)'''
        currency = company.currency_id.id
        partner = move.picking_id and move.picking_id.partner_id
        if partner:
            code = self.get_code_from_locs(move)
            if partner.property_product_pricelist and code == 'outgoing':
                currency = partner.property_product_pricelist.currency_id.id
        return partner, self._uid, currency

    @api.multi
    def _create_invoice_line_from_vals(self, move, invoice_line_vals):
        return self.env['account.invoice.line'].create(invoice_line_vals)

    @api.multi
    def _get_price_unit_invoice(self, move_line, type):
        """ Gets price unit for invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: The price unit for the move line
        """
        if type in ('in_invoice', 'in_refund'):
            return move_line.price_unit
        else:
            # If partner given, search price in its sale pricelist
            if move_line.partner_id and \
                    move_line.partner_id.property_product_pricelist:
                pricelist_obj = self.pool.get("product.pricelist")
                pricelist = move_line.partner_id.property_product_pricelist.id
                price = pricelist_obj.price_get(
                    [pricelist], move_line.product_id.id,
                    move_line.product_uom_qty, move_line.partner_id.id, {
                            'uom': move_line.product_uom.id,
                            'date': move_line.date,
                            })[pricelist]
                if price:
                    return price
        return move_line.product_id.lst_price

    @api.multi
    def _get_moves_taxes(self, moves, inv_type):
        extra_move_tax = {}
        is_extra_move = {}
        for move in moves:
            if move.picking_id:
                is_extra_move[move.id] = True
                if not (move.picking_id, move.product_id) in extra_move_tax:
                    extra_move_tax[move.picking_id, move.product_id] = 0
            else:
                is_extra_move[move.id] = False
        return is_extra_move, extra_move_tax

    @api.multi
    def action_cancel(self):
        res = super(StockMove, self).action_cancel()
        self.write({'invoice_state': 'none'})
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    @api.depends('move_lines')
    def _get_invoice_state(self):
        for pick in self:
            result = 'none'
            for move in pick.move_lines:
                if move.invoice_state == 'invoiced':
                    result = 'invoiced'
                elif move.invoice_state == '2binvoiced':
                    result = '2binvoiced'
                    break
            pick.invoice_state = result

    @api.multi
    def _set_inv_state(self):
        for record in self:
            # pick = record.browse(picking_id)
            moves = [x.id for x in record.move_lines]
            move_obj = record.env['stock.move']
            move_obj.write({'invoice_state': record.state})

    invoice_state = fields.Selection(
        [("invoiced", "Invoiced"),
         ("2binvoiced", "To Be Invoiced"),
         ("none", "Not Applicable")],
        string="Invoice Control", required=True,
        compute=_get_invoice_state,
        inverse=_set_inv_state,
        store=True,
        default='none'
        )

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        ''' This function simply creates the invoice from the given values.
         It is overriden in delivery module to add the delivery costs.
        '''
        invoice_obj = self.env['account.invoice']
        return invoice_obj.create(vals)

    @api.multi
    def _get_partner_to_invoice(self, picking):
        """ Gets the partner that will be invoiced
            Note that this function is inherited in the sale
            and purchase modules @param picking: object of the
             picking for which we are selecting the partner to invoice
            @return: object of the partner to invoice
        """
        return picking.partner_id and picking.partner_id.id

    @api.multi
    def action_invoice_create(
            self, active_ids, journal_id, group=False, type='out_invoice'):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        todo = {}
        for picking_id in active_ids:
            picking = self.env['stock.picking'].browse(picking_id)
            partner = self.with_context(
                type=type)._get_partner_to_invoice(picking)
            # grouping is based on the invoiced partner
            if group:
                key = partner
            else:
                key = picking.id
            for move in picking.move_lines:
                if move.invoice_state == '2binvoiced':
                    if (move.state != 'cancel') and not move.scrapped:
                        todo.setdefault(key, [])
                        todo[key].append(move)
        invoices = []
        for moves in todo.values():
            invoices += self._invoice_create_line(
                active_ids, moves, journal_id, type)
        return invoices

    @api.multi
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        partner, currency_id, company_id, user_id = key
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable_id.id
            payment_term = partner.property_payment_term_id.id or False
        else:
            account_id = partner.property_account_payable_id.id
            payment_term = \
                partner.property_supplier_payment_term_id.id or False
        return {
            'origin': move.picking_id.name,
            'date_invoice': self.env.context.get('date_inv', False),
            'user_id': user_id,
            'partner_id': partner.id,
            'account_id': account_id,
            'payment_term_id': payment_term,
            'type': inv_type,
            'fiscal_position_id': partner.property_account_position_id.id,
            'company_id': company_id,
            'currency_id': currency_id,
            'journal_id': journal_id,
        }

    @api.multi
    def _invoice_create_line(
            self, picking_ids, moves, journal_id, inv_type='out_invoice'):

        invoice_obj = self.env['account.invoice']
        move_obj = self.env['stock.move']
        invoices = {}
        is_extra_move, extra_move_tax = move_obj._get_moves_taxes(
            moves, inv_type)

        for move in moves:
            company = move.company_id
            origin = move.picking_id.name
            partner, user_id, currency_id = move_obj._get_master_data(
                move, company)

            key = (partner, currency_id, company.id, self._uid)
            invoice_vals = self._get_invoice_vals(
                key, inv_type, journal_id, move)

            if key not in invoices:
                # Get account and payment terms
                invoice_id = self._create_invoice_from_picking(
                    move.picking_id, invoice_vals)
                invoices[key] = invoice_id
            else:
                invoice = invoices[key]
                merge_vals = {}
                if not invoice.origin or invoice_vals[
                        'origin'] not in invoice.origin.split(', '):
                    invoice_origin = filter(
                        None, [invoice.origin, invoice_vals['origin']])
                    merge_vals['origin'] = ', '.join(invoice_origin)
                if invoice_vals.get('name', False) and\
                        (not invoice.name or invoice_vals['name'] not in
                         invoice.name.split(', ')):
                    invoice_name = filter(
                        None, [invoice.name, invoice_vals['name']])
                    merge_vals['name'] = ', '.join(invoice_name)
                if merge_vals:
                    invoice.write(merge_vals)

            move.write({'invoice_state': 'invoiced'})

        invoice_line_tmp = []
        result_invoice_line = []
        if invoice_id:
            for picking_id in picking_ids:
                dict_onchange = invoice_id.play_onchanges(
                    {'picking_id': picking_id},
                    ['picking_id'],
                )

                invoice_line_tmp.append(dict_onchange['invoice_line_ids'])

                # Key tax_line_ids from return dict is ignoring because
                #  method compute_taxes() filled the field

                picking_obj = self.env['stock.picking'].browse(picking_id)
                picking_obj.invoice_state = 'invoiced'

            for invoice_line in invoice_line_tmp:
                index = 0
                while index < len(invoice_line):
                    for line in invoice_line[index]:
                        if type(line) is dict:
                            result_invoice_line.append([0, 0, line])
                    index += 1

            invoice_id.write({'invoice_line_ids': result_invoice_line})
            invoice_id.compute_taxes()

        return invoices.values()

    @api.multi
    def _prepare_values_extra_move(self, op, product, remaining_qty):
        """
        Need to pass invoice_state of picking when an extra move is
         created which is not a copy of a previous
        """
        res = super(StockPicking, self)._prepare_values_extra_move(
            op, product, remaining_qty)
        res.update({'invoice_state': op.picking_id.invoice_state})
        if op.linked_move_operation_ids:
            res.update({
                'price_unit':
                    op.linked_move_operation_ids[-1].move_id.price_unit})
        return res
