# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    lines_sorted_by_picking_ids = fields.One2many(
        comodel_name='account.invoice.line',
        compute='_compute_lines_picking_sorted_ids',
        readonly=True,
        string='Invoice Lines')

    @api.multi
    def _compute_lines_sorted_by_picking_ids(self):
        for invoice in self:
            invoice.lines_sorted_by_picking_ids = (
                invoice.invoice_line_ids.sorted(key=lambda x: (
                    x.sale_line_id.procurement_id.move_id.picking_id.write_date)))

    @api.multi
    def lines_grouped_by_picking(self):
        self.ensure_one()
        group = {}
        for line in self.invoice_line_ids:
            pick = line.sale_line_id.procurement_id.move_id.picking_id
            if pick not in group:
                group[pick] = []
            group[pick].append(line)
        return [{'picking': pick, 'lines': group[pick]} for pick in sorted(
            group.keys(), key=lambda k: k.write_date)]


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sale_move_link_ids = fields.One2many(
        comodel_name='sale.order.line.stock.move',
        inverse_name='invoice_line_id',
    )
