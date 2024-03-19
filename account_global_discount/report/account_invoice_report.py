from odoo import api, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    @api.model
    def _where(self):
        where_str = super()._where()
        return where_str.replace(
            "NOT line.exclude_from_invoice_tab",
            "(NOT line.exclude_from_invoice_tab OR global_discount_item = true)",
        )
