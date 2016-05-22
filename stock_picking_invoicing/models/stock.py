# -*- coding: utf-8 -*-
# © 2016 <OCA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)

INVOICE_STATE = [
    ("invoiced", "Invoiced"),
    ("2binvoiced", "To Be Invoiced"),
    ("none", "Not Applicable")
    ]


class StockLocationPath(models.Model):
    _inherit = "stock.location.path"
    
    invoice_state = fields.Selection(INVOICE_STATE, 
                                     string="Invoice Status", default="none")
    
    
    @api.v7
    def _prepare_push_apply(self, cr, uid, rule, move, context=None):
        res = super(StockLocationPath, self)._prepare_push_apply(cr, uid, rule, move, context=context)
        res['invoice_state'] = rule.invoice_state or 'none'
        return res


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'
    
    invoice_state = fields.Selection(INVOICE_STATE, 
                                     string="Invoice Status", default="none")


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"
    
    
    invoice_state = fields.Selection(INVOICE_STATE, 
                                     string="Invoice Status", default="none")

#    @api.v7
#    def _run_move_create(self, cr, uid, procurement, context=None):
#        res = super(ProcurementOrder, self)._run_move_create(cr, uid, procurement, context=context)
#        res.update({'invoice_state': procurement.rule_id.invoice_state or procurement.invoice_state or 'none'})
#        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    #=====================
    # FIELDS
    #=====================
    
    invoice_state = fields.Selection(INVOICE_STATE, 
                                     string="Invoice Status"
                                     , default="none"
                                     )

    invoice_line_id = fields.Many2one('account.invoice.line', string='Invoice Line')
    invoice_id = fields.Many2one('account.invoice', string='Invoice', 
                                 related='invoice_line_id.invoice_id')

    
    #=====================
    # Business Logic
    #=====================

    @api.model
    def _create_invoice_line_from_vals(self, invoice_line_vals):
        return self.env['account.invoice.line'].create(invoice_line_vals)

    @api.model
    def _get_master_data(self, move, company):    
        ''' returns a tuple (browse_record(res.partner), ID(res.users), ID(res.currency)'''
        currency = company.currency_id.id
        partner = move.picking_id and move.picking_id.partner_id
        if partner:
            code = self.get_code_from_locs(move)
            if partner.property_product_pricelist and code == 'outgoing':
                currency = partner.property_product_pricelist.currency_id.id
        data = partner, self.env.uid, currency
        
        if move.picking_id.partner_id.id != data[0].id:
            # if someone else modified invoice partner, I use it
            return data
        
        partner_invoice_id = move.picking_id.partner_id.address_get(
                                                                    ['invoice'])['invoice']
        partner = self.env['res.partner'].browse(partner_invoice_id)
        new_data = partner, data[1], data[2]
        return new_data
        
    @api.multi
    def _get_taxes(self, fiscal_position):
        self.ensure_one()
        taxes_ids = self.product_id.taxes_id        
        my_taxes = taxes_ids.filtered(lambda r: r.company_id.id == self.env.context['force_company'])    
        my_taxes = fiscal_position.map_tax(my_taxes)
        my_taxes = [t.id for t in my_taxes]
        
        return my_taxes
    
    @api.multi
    def _get_account(self, fiscal_position, account_id):
        self.ensure_one()
        account_id = fiscal_position.map_account(account_id)
        
        return account_id

    @api.multi
    def _get_invoice_line_vals(self, partner, inv_type):
        self.ensure_one()
        fp_obj = self.env['account.fiscal.position']
        context = self.env.context
        
        # Get account_id
        fp = fp_obj.browse(cr, uid, context.get('fp_id')) if context.get('fp_id') else False
        name = False
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = self.product_id.property_account_income_id.id
            if not account_id:
                account_id = self.product_id.categ_id.property_account_income_categ_id.id
            if self.procurement_id and self.procurement_id.sale_line_id:
                name = self.procurement_id.sale_line_id.name
        else:
            account_id = self.product_id.property_account_expense_id.id
            if not account_id:
                account_id = self.product_id.categ_id.property_account_expense_categ_id.id
        fiscal_position = fp or partner.property_account_position_id
        
        account_id = self._get_account(fiscal_position, account_id)  

        # set UoS if it's a sale and the picking doesn't have one
        uos_id = self.product_uom.id
        quantity = self.product_uom_qty
#        if move.product_uos:
#            uos_id = move.product_uos.id
#            quantity = move.product_uos_qty
            
                
        taxes_ids = self._get_taxes(fiscal_position)

        res = {
            'name': name or (self.picking_id.name + '\n' +  self.name),
            'account_id': account_id,
            'product_id': self.product_id.id,
            'uos_id': uos_id,
            'uom_id': uos_id,
            'quantity': quantity,
            'price_unit': self._get_price_unit_invoice(inv_type, partner),
            'invoice_line_tax_ids': [(6, 0, taxes_ids)],
            'discount': 0.0,
            'account_analytic_id': False,
        }

        # negative value on quantity
        if ((inv_type == 'out_invoice' and
            self.location_id.usage == 'customer') or
            (inv_type == 'out_refund' and
            self.location_dest_id.usage == 'customer') or
            (inv_type == 'in_invoice' and
            self.location_dest_id.usage == 'supplier') or
            (inv_type == 'in_refund' and
            self.location_id.usage == 'supplier')):
            res['quantity'] *= -1

        return res
        
        
    @api.multi
    def _get_price_unit_invoice(self, inv_type, partner):
        """ Gets price unit for invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: The price unit for the move line
        """
        result = 0.0
        if inv_type in ('in_invoice', 'in_refund'):
            return self.product_id.price        
        else:
            # If partner given, search price in its sale pricelist
            
            if partner and partner.property_product_pricelist:
                product_id = self.product_id.with_context(
                                         partner=self.partner_id.id,
                                         quantity=self.product_uom_qty,
                                         date=self.date,
                                         pricelist=partner.property_product_pricelist.id,
                                         uom=self.product_uom.id
                                        )                
                result = product_id.price                
            else :                
                result = product_id.lst_price
        
        return result
    
    @api.multi
    def _get_moves_taxes(self, moves, inv_type):
        
        #extra moves with the same picking_id and product_id of a move have the same taxes
        extra_move_tax = {}
        is_extra_move = {}
        for move in moves:
            if move.picking_id:
                is_extra_move[move.id] = True
                if not (move.picking_id, move.product_id) in extra_move_tax:
                    extra_move_tax[move.picking_id, move.product_id] = 0
            else:
                is_extra_move[move.id] = False
        return (is_extra_move, extra_move_tax)
    

class StockPicking(models.Model):
    _inherit = "stock.picking"

    #===========================
    # Views
    #===========================
    
    @api.multi
    def set_to_be_invoiced(self):
        for picking in self:
            if picking.invoice_state == '2binvoiced':
                raise UserError(_("Invoice control cannot be updated for picking %s as it is already set as \"To be invoiced\"") % picking.name)
            if picking.invoice_state in ('none', 'invoiced'):
                if picking.invoice_id:
                    raise UserError(_("Picking %s is already linked to invoice %s") %
                                  (picking.name, picking.invoice_id.number))
            picking.invoice_state = '2binvoiced'
            for move in picking.move_lines:
                if move.invoice_state != 'invoiced':
                    move.invoice_state = '2binvoiced'
        return True
    
    @api.multi
    def set_invoiced(self):
        for picking in self:
            if picking.invoice_state == 'invoiced' or picking.invoice_id :
                raise UserError(_("Invoice control cannot be updated for picking %s as it is already set as \"Invoiced\"") % picking.name)
            if picking.invoice_state in ('2binvoiced'):
                if picking.invoice_id:
                    raise UserError(_('Picking %s is already linked to invoice %s') %
                                  (picking.name, picking.invoice_id.number))
            picking.invoice_state = '2binvoiced'
            for move in picking.move_lines:
                if move.invoice_state != 'invoiced':
                    move.invoice_state = '2binvoiced'
        return True

    #=====================
    # FIELDS
    #=====================

    invoice_state = fields.Selection(INVOICE_STATE, 
                                     string="Invoice Status"
                                     , default="none"
                                     )
    
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    
    
    #=====================
    # Business Logic
    #=====================
    
    @api.multi
    def _create_invoice_from_picking(self, picking, vals):
        ''' This function simply creates the invoice from the given values. It is overriden in delivery module to add the delivery costs.
        '''
        invoice_obj = self.env['account.invoice']
        _logger.debug("Create invoice with %s" % vals)
        return invoice_obj.create(vals)
    
    @api.model
    def _get_partner_to_invoice(self):
        partner_obj = self.env['res.partner']
  
        partner = self.partner_id 

        return partner.address_get(['invoice'])['invoice']

    @api.multi
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        partner, currency_id, company_id, user_id = key
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable_id.id
            payment_term = partner.property_payment_term_id.id or False
        else:
            account_id = partner.property_account_payable_id.id
            payment_term = partner.property_supplier_payment_term_id.id or False
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

    
    @api.model
    def _invoice_create_line(self, moves, journal_id, inv_type='out_invoice'):
        """
        Create an invoice and associated lines
        """
        invoice_obj = self.env['account.invoice']
        move_obj = self.env['stock.move']
        invoices = {}
        
        is_extra_move, extra_move_tax = move_obj._get_moves_taxes(moves, inv_type)
        product_price_unit = {}
        _logger.debug("COntexte %s" % self.env.context)
        invoice_id = None
        company_id  =  self.env.context['force_company'] or self.env['res.users']._get_company() 
        for move in moves:
            company = self.env['res.company'].search([('id', '=', company_id)])
            origin = move.sudo().picking_id.name
            partner, user_id, currency_id = move_obj._get_master_data(move, company)
            key = (partner, currency_id, company.id, user_id)
            _logger.debug("contexte %s" % self.env.context)
            invoice_vals = self._get_invoice_vals(key, inv_type, journal_id, move)
            if key not in invoices:
                # Get account and payment terms
                _logger.debug("Add invoice to list")
                invoice_id = self._create_invoice_from_picking(move.picking_id, invoice_vals)
                invoices[key] = invoice_id.id
                _logger.debug("Add invoice to list after key")
            else:
                _logger.debug("Add found invoice to list")
                invoice = invoice_obj.search([('id', '=', invoices[key])])
                merge_vals = {}
                if not invoice.origin or invoice_vals['origin'] not in invoice.origin.split(', '):
                    invoice_origin = filter(None, [invoice.origin, invoice_vals['origin']])
                    merge_vals['origin'] = ', '.join(invoice_origin)
                    
                if invoice_vals.get('name', False) and (not invoice.name or invoice_vals['name'] not in invoice.name.split(', ')):
                    invoice_name = filter(None, [invoice.name, invoice_vals['name']])
                    merge_vals['name'] = ', '.join(invoice_name)
                if merge_vals:
                    _logger.debug("Merge vues %s" % merge_vals)
                    invoice.write(merge_vals)

            move.with_context(
                              fp_id=invoice_vals.get('fiscal_position_id', False),
                              )
            
            invoice_line_vals = move._get_invoice_line_vals(partner, inv_type)
            invoice_line_vals['invoice_id'] = invoices[key]
            invoice_line_vals['origin'] = origin
            if not is_extra_move[move.id]:
                product_price_unit[invoice_line_vals['product_id'], invoice_line_vals['uos_id']] = invoice_line_vals['price_unit']
            if is_extra_move[move.id] and (invoice_line_vals['product_id'], invoice_line_vals['uos_id']) in product_price_unit:
                invoice_line_vals['price_unit'] = product_price_unit[invoice_line_vals['product_id'], invoice_line_vals['uos_id']]
            if is_extra_move[move.id]:
                desc = (inv_type in ('out_invoice', 'out_refund') and move.product_id.product_tmpl_id.description_sale) or \
                    (inv_type in ('in_invoice', 'in_refund') and move.product_id.product_tmpl_id.description_purchase)
                invoice_line_vals['name'] += ' ' + desc if desc else ''
                if extra_move_tax[move.picking_id, move.product_id]:
                    invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[move.picking_id, move.product_id]
                #the default product taxes
                elif (0, move.product_id) in extra_move_tax:
                    invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[0, move.product_id]

            invoice_line = move._create_invoice_line_from_vals(invoice_line_vals)
            _logger.debug("Before invoicing write")
            if invoice_line :
                move.write({'invoice_line_id': invoice_line.id,
                            'invoice_state': 'invoiced'
                })
            if move.picking_id and not move.picking_id.invoice_id :
                move.picking_id.write({'invoice_id': invoice_id.id,
                                    'invoice_state': 'invoiced'
                })
                
        
        invoice_id.compute_invoice_tax_lines()

#        invoice_obj.button_compute(cr, uid, invoices.values(), context=context, set_total=(inv_type in ('in_invoice', 'in_refund')))
#       
        
        return invoices.values()
    

    
    @api.model
    def action_invoice_create(self, ids, journal_id, group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        
        todo = {}
        
        pickings = self.search([('id', 'in', ids)])
        for picking in pickings:
            partner = self._get_partner_to_invoice()
            #grouping is based on the invoiced partner
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
            invoices += self._invoice_create_line(moves, journal_id, type)
        
        
        
        return invoices