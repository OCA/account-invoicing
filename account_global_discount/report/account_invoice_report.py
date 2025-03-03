from odoo import api, models, tools


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    @api.model
    def _where(self):
        where_sql = super()._where()
        where_sql_str = where_sql.code.replace(
            "NOT line.exclude_from_invoice_tab",
            "(NOT line.exclude_from_invoice_tab "
            "OR invoice_global_discount_id is not null)",
        )
        return tools.SQL(where_sql_str)
