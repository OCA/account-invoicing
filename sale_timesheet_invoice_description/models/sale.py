# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    timesheet_invoice_description = fields.Selection(
        '_get_timesheet_invoice_description', default='111')

    @api.model
    def _get_timesheet_invoice_description(self):
        return [
            ('111', _('Date - Time spent - Description')),
            ('101', _('Date - Description')),
            ('001', _('Description')),
            ('011', _('Time spent - Description')),
        ]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line_details(self, line, desc_rule):
        details = []
        if desc_rule[0] == '1':
            details.append(line.date)
        if desc_rule[1] == '1':
            details.append(
                "%s %s" % (line.unit_amount, line.product_uom_id.name))
        if desc_rule[2] == '1':
            details.append(line.name)
        return details

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        desc_rule = self.order_id.timesheet_invoice_description
        note = []
        for line in self.env['account.analytic.line'].search(
                [('so_line', '=', self.id)]):
            details = self._prepare_invoice_line_details(line, desc_rule)
            note.append(
                u' - '.join(map(lambda x: unicode(x) or '', details)))
        if note:
            res['name'] += "\n" + (
                "\n".join(map(lambda x: unicode(x) or '', note)))
        return res
