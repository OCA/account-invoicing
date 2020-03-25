from odoo import fields, models

class Invoice(models.Model):
    _inherit = 'account.invoice'

    def _get_order(self):
        for invoice in self:
            order_ids = []
            for line in invoice.invoice_line_ids:
                order_ids.append(line.sale_line_ids.order_id.id)
            invoice.sale_order_ids = [(6, 0, list(set(order_ids)))]

    sale_order_ids = fields.Many2many('sale.order', compute='_get_order')
