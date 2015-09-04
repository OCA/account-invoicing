# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api, fields


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    group_type = fields.Selection(
        [('group_by_product', 'Group by product'),
         ('group_by_product_category', 'Group by product category')
         ],
        string='Group Type',
    )

    @api.model
    def _group_moves_by_group_type(self, moves, group_type):
        """Return moves grouped by group_type"""
        grouped_moves = {}
        for move in moves:
            if group_type == 'group_by_product':
                key = (move._get_partner_id(), move._get_product_id())
            else:
                key = (move._get_partner_id(), move._get_categ_id())
            if key not in grouped_moves:
                grouped_moves[key] = []
            grouped_moves[key].append(move)
        return grouped_moves

    @api.multi
    def create_invoice(self):
        if self.group_type:
            journal2type = {
                'sale': 'out_invoice',
                'purchase': 'in_invoice',
                'sale_refund': 'out_refund',
                'purchase_refund': 'in_refund'}
            inv_type = journal2type.get(self.journal_type) or 'out_invoice'
            picking_ids = self.env.context['active_ids']
            picking_model = self.env['stock.picking']
            pickings = picking_model.browse(picking_ids)
            moves = []
            for picking in pickings:
                for move in picking.move_lines:
                    moves.append(move)
            invoices = []
            moves_by_group_type = self._group_moves_by_group_type(
                moves, self.group_type)
            for moves in moves_by_group_type.values():
                invoices += picking_model.with_context(
                    date_inv=self.invoice_date,
                    inv_type=inv_type)._invoice_create_line(
                        moves, self.journal_id.id, inv_type)
            return invoices
        else:
            return super(StockInvoiceOnshipping, self).create_invoice()
