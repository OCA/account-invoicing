# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import config


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    timesheet_invoice_description = fields.Selection(
        '_get_timesheet_invoice_description', default='000')

    @api.model
    def _get_timesheet_invoice_description(self):
        return [
            ('000', _('None')),
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
        if not desc_rule or desc_rule == '000':
            return res
        note = []
        domain = [('so_line', '=', self.id)]
        last_invoice = self.invoice_lines.sorted(lambda x: x.create_date)[-1:]
        if last_invoice:
            domain.append(('create_date', '>', last_invoice.create_date))
        for line in self.env['account.analytic.line'].search(
                domain, order='date, id'):
            details = self._prepare_invoice_line_details(line, desc_rule)
            note.append(
                u' - '.join(map(lambda x: str(x) or '', details)))
        # This is for not breaking possible tests that expects to create the
        # invoices lines the standard way
        if note and (not config['test_enable'] or self.env.context.get(
                'test_timesheet_description')):
            res['name'] += "\n" + (
                "\n".join(map(lambda x: str(x) or '', note)))
        return res
