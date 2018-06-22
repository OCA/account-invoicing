# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools import float_is_zero


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    move_invoice_link_ids = fields.One2many(
        comodel_name='sale.order.line.stock.move',
        inverse_name='sale_line_id',
    )

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        """
        Overwrite original function to create one invoice line for each move.

        :param invoice_id: integer
        :param qty: float quantity to invoice
        """
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        if float_is_zero(qty, precision_digits=precision):
            return
        for line in self:
            moves_links = line.move_invoice_link_ids.filtered(
                lambda x: not x.invoice_line_id)
            for move_link in moves_links:
                # If return move inverse sign
                move_qty = move_link.move_id.product_uom_qty * (
                    move_link.move_id.location_id.usage == 'customer' and
                    -1.0 or 1.0)
                vals = line._prepare_invoice_line(qty=move_qty)
                qty -= move_qty
                vals.update({'invoice_id': invoice_id,
                             'sale_line_ids': [(6, 0, [line.id])]})
                inv_line = self.env['account.invoice.line'].create(vals)
                move_link.invoice_line_id = inv_line
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(qty=qty)
                vals.update({'invoice_id': invoice_id,
                             'sale_line_ids': [(6, 0, [line.id])]})
                self.env['account.invoice.line'].create(vals)


class SaleOrderLineStockMove(models.Model):
    _name = 'sale.order.line.stock.move'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Order Line')
    move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Move')
    invoice_line_id = fields.Many2one(
        comodel_name='account.invoice.line',
        string='Invoice Line')


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        result = super(StockMove, self).action_done()
        SaleOrderLineStockMove = self.env['sale.order.line.stock.move']
        for move in self.filtered(lambda x: x.procurement_id.sale_line_id and (
                x.product_id.invoice_policy == 'delivery')):
            SaleOrderLineStockMove.create({
                'move_id': move.id,
                'sale_line_id': move.procurement_id.sale_line_id.id
            })
        return result
