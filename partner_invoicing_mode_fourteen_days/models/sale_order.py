# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.fields import Datetime
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def cron_generate_fourteen_days_invoices(self):
        company_ids = self._get_companies_fourteen_days_invoicing()
        if company_ids:
            self.generate_fourteen_days_invoices(companies=company_ids)

    @api.model
    def generate_fourteen_days_invoices(self, companies=None):
        return self.generate_invoices(
            companies,
            invoicing_mode="fourteen_days",
            last_execution_field="invoicing_mode_fourteen_days_last_execution",
        )

    def _get_generate_invoices_domain(self, companies, invoicing_mode="standard"):
        today = Datetime.now()
        domain = super()._get_generate_invoices_domain(
            companies, invoicing_mode=invoicing_mode
        )
        if invoicing_mode == "fourteen_days":
            # We use the next_invoice_date field to generate it
            fourteen_domain = [
                "|",
                ("partner_invoice_id.next_invoice_date", "=", False),
                ("partner_invoice_id.next_invoice_date", "<=", today),
            ]
            return expression.AND([domain, fourteen_domain])
        return domain

    @api.model
    def _get_companies_fourteen_days_invoicing(self):
        """
        Get company ids for which today is ten days invoicing day
        (10/20/last day of month).
        """
        today = Datetime.now()
        domain = [
            "|",
            ("invoicing_mode_fourteen_days_last_execution", "<", today),
            ("invoicing_mode_fourteen_days_last_execution", "=", False),
        ]
        return self.env["res.company"].search(domain)
