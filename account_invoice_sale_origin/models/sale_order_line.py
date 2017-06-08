# -*- coding: utf-8 -*-
# © 2015 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def invoice_line_create(self):
        origin = self.mapped('order_id.name')[0]
        invoice_line_ids = super(SaleOrderLine, self).invoice_line_create()
        invoice_line_model = self.env['account.invoice.line']
        invoice_lines = invoice_line_model.browse(invoice_line_ids)
        invoice_lines.write({'origin': origin})
        return invoice_line_ids
