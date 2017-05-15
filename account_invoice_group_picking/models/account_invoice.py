# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models, tools


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    @tools.ormcache('picking', 'order')
    def _prepare_picking_info(self, picking, order, inv_line):
        res = order and _('Order: %s') % order.name or ''
        if picking:
            res = _('%s Picking: %s %s') % (
                res, picking.date_done[:10], picking.name)
        return res

    @api.model
    def _sort_grouped_lines(self, lines_dic):
        return sorted(lines_dic, key=lambda x: (
            x['order'].date_order, x['picking'].date_done))

    @api.multi
    def lines_grouped_by_picking(self):
        self.ensure_one()
        res = []
        for line in self.invoice_line_ids:
            pick = line.sale_move_link_ids.mapped('move_id.picking_id')[:1]
            if not pick:
                picks = line.sale_line_ids.mapped(
                    'procurement_ids.move_ids.picking_id')
                pick = picks.filtered(lambda x: (
                    x.state == 'done' and
                    line.product_id in x.move_lines.mapped('product_id')))[:1]
            order = line.sale_line_ids.order_id
            res.append({'line': line, 'picking': pick,
                        'order': order,
                        'picking_info':
                            self._prepare_picking_info(pick, order, line),
                        })
        return self._sort_grouped_lines(res)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sale_move_link_ids = fields.One2many(
        comodel_name='sale.order.line.stock.move',
        inverse_name='invoice_line_id',
    )
