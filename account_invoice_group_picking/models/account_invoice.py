# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def lines_grouped_by_picking(self):
        self.ensure_one()
        res = []
        for line in self.invoice_line_ids:
            pick = (line.sale_move_link_ids[:1].move_id.picking_id or
                    line.sale_line_ids.procurement_ids.move_ids[:1].picking_id)

            res.append((line, pick))
        return sorted(res, key=lambda x: x[1].write_date)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sale_move_link_ids = fields.One2many(
        comodel_name='sale.order.line.stock.move',
        inverse_name='invoice_line_id',
    )
