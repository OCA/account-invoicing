# -*- coding: utf-8 -*-
# Copyright 2017 Akretion
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    picking_id = fields.Many2one(
        'stock.picking',
        string='Add Picking Order',
        help="When selected, the associated picking order lines are added "
        "to the vendor bill. Several Pickings can be selected.")

    # code inspired from _onchange_allowed_purchase_ids in purchase module
    # TODO extract reusable bit
    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_picking_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        picking orders.
        '''
        result = {}

        # A Picking can be selected only if at least one PO line is not already
        # in the invoice
        move_line_ids = self.invoice_line_ids.mapped('move_line_id')
        picking_ids = self.invoice_line_ids.mapped('picking_id').filtered(
            lambda r: r.move_lines <= move_line_ids)

        if self.type in ['out_invoice', 'in_refund']:
            picking_type = ['outgoing', 'internal']
        elif self.type in ['in_invoice', 'out_refund']:
            picking_type = ['incoming', 'internal']

        result['domain'] = {
            'picking_id': [
                ('state', '=', 'done'),
                ('picking_type_id.code', 'in', picking_type),
                ('partner_id', '!=', False),
                ('partner_id', 'child_of', self.partner_id.id),
                ('id', 'not in', picking_ids.ids),
            ],
        }
        # TODO we can still select a picking linked to a sale
        # order already invoiced from the sale order
        # we should filter out picking with a sale_id.invoice_status
        # different than 'to_invoice' but only if there is a sale_id
        # ('sale_id.invoice_status', '=', 'to invoice'),
        return result

    def _prepare_invoice_line_from_stock_move(self, line):
        if hasattr(line, 'purchase_line_id') and line.purchase_line_id:
            # we let the purchase order line prepare the invoice line
            data = self._prepare_invoice_line_from_po_line(
                line.purchase_line_id)
            data['move_line_id'] = line.id  # this avoids adding the line again
            return data
        elif (hasattr(line, 'procurement') and
                line.procurement_id and line.procurement_id.sale_line_id):
            # we let the sale order line prepare the invoice line
            sale_line = line.procurement_id.sale_line_id
            data = sale_line._prepare_invoice_line(sale_line.qty_to_invoice)
            data['sale_line_ids'] = [(6, 0, [sale_line.id])]
            data['move_line_id'] = line.id  # this avoids adding the line again
            return data

        qty = line.product_uom_qty
        taxes = line.product_id.taxes_id
        invoice_line_tax_ids = self.fiscal_position_id.map_tax(taxes)
        invoice_line = self.env['account.invoice.line']
        if line.picking_id.picking_type_id.code in ['incoming', 'internal']:
            price_unit = line.product_id.standard_price
        else:
            price_unit = line.product_id.list_price
        data = {
            'move_line_id': line.id,
            'name': line.product_id.name,
            'origin': line.picking_id.origin or line.picking_id.name,
            'uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context(
                {'journal_id': self.journal_id.id, 'type': 'in_invoice'}
            )._default_account(),
            'price_unit': price_unit,
            'quantity': qty,
            'discount': 0.0,
            'invoice_line_tax_ids': invoice_line_tax_ids.ids
        }
        account = invoice_line.get_invoice_line_account(
            'in_invoice', line.product_id, self.fiscal_position_id,
            self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data

    # Load all unsold Picking lines
    # (code inspired from purchase_order_change from purchase module)
    @api.onchange('picking_id')
    def picking_change(self):
        if not self.picking_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.picking_id.partner_id.id

        new_lines = self.env['account.invoice.line']
        existing_lines = self.invoice_line_ids.mapped('move_line_id')
        for line in self.picking_id.move_lines - existing_lines:
            data = self._prepare_invoice_line_from_stock_move(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.picking_id = False
        return {}


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # These fields are used to link back to the original move/picking
    # so that these invoice lines cannot be generated again.
    move_line_id = fields.Many2one(
        'stock.move',
        'Stock Move',
        ondelete='set null',
        index=True,
        readonly=True)
    picking_id = fields.Many2one(
        'stock.picking',
        related='move_line_id.picking_id',
        string='Stock Picking',
        store=False,
        readonly=True,
        related_sudo=False,
        help="Associated Stock Picking. Filled in automatically when "
        "a Picking is chosen on the vendor bill.")
