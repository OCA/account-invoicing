# -*- coding: utf-8 -*-
# Copyright 2016 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api, fields
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


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
            partner = move.picking_id.partner_id
            product = move.product_id
            categ = product.categ_id
            if group_type == 'group_by_product':
                key = (partner.id, product.id)
            elif group_type == 'group_by_product_category':
                key = (partner.id, categ.id)
            else:
                raise ValidationError(_(
                    'The selected group type is not accepted.'))
            if key not in grouped_moves:
                grouped_moves[key] = []
            grouped_moves[key].append(move)
        return grouped_moves

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        if self.group_type:
            if self.group:
                raise ValidationError(_(
                    'It is not allowed to select multiple grouping options.'))
            journal2type = {
                'sale': 'out_invoice',
                'purchase': 'in_invoice',
                'sale_refund': 'out_refund',
                'purchase_refund': 'in_refund'}
            inv_type = journal2type.get(self.journal_type) or 'out_invoice'
            picking_ids = self.env.context['active_ids']
            picking_model = self.env['stock.picking']
            pickings = picking_model.browse(picking_ids)
            moves = pickings.mapped('move_lines')
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

    @api.multi
    @api.onchange('group')
    def onchange_group(self):
        self.ensure_one()
        if self.group:
            self.group_type = None

    @api.multi
    @api.onchange('group_type')
    def onchange_group_type(self):
        self.ensure_one()
        if self.group_type:
            self.group = False
