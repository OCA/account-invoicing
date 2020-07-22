from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def split_quotation(self):
        self.ensure_one()
        new_invoice = self.copy()
        new_invoice.split_id = self.id
        new_invoice.date_due = self.date_due
        origin_lines = self.invoice_line_ids.sorted(
            lambda l: (l.product_id, l.price_total)
        )
        new_lines = new_invoice.invoice_line_ids.sorted(
            lambda l: (l.product_id, l.price_total)
        )

        for origin_line, new_line in zip(origin_lines, new_lines):
            if not new_line.split:
                new_line.unlink()
            else:
                new_line.split = False
                new_line.sale_line_ids = origin_line.sale_line_ids
                origin_line.unlink()
        return new_invoice
