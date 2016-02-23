# -*- coding: utf-8 -*-

from openerp import models, fields, api


class sale_order(models.Model):

    _inherit = 'sale.order'

    price_include = fields.Boolean(
        string='Tax Included in Price',
        readonly=True,
        compute="_price_include")

    @api.one
    @api.depends('order_line.tax_id')
    def _price_include(self):
        self.price_include = self.order_line and \
            self.order_line[0].tax_id and \
            self.order_line[0].tax_id[0].price_include or False

    @api.model
    def _append_invoice_line(self, invoice, lines):
        if invoice.is_deposit:
            lines = super(sale_order, self)._append_invoice_line(invoice,
                                                                 lines)
        return lines

    @api.model
    def _selected_invoice_lines(self, order, states):
        """ Overwrite (ok) on a hook method """
        lines = []
        for line in order.order_line:
            if line.invoiced and \
                    not self._context.get('invoice_plan_percent', False):
                continue
            elif (line.state in states):
                lines.append(line.id)
        return lines

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
