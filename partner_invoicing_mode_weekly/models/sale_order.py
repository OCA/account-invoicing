# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models
from odoo.fields import Datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def cron_generate_weekly_invoices(self):
        company_ids = self._get_companies_weekly_invoicing()
        if company_ids:
            self.generate_invoices(
                company_ids,
                invoicing_mode="weekly",
                last_execution_field="invoicing_mode_weekly_last_execution",
            )

    @api.model
    def generate_weekly_invoices(self, companies=None):
        # TODO: Kept former function for backward compatibility. To remove
        # in further version.
        return self.generate_invoices(
            companies,
            invoicing_mode="weekly",
            last_execution_field="invoicing_mode_weekly_last_execution",
        )

    @api.model
    def _get_companies_weekly_invoicing(self):
        """Get company ids for which today is weekly invoicing day."""
        today = Datetime.now()
        domain = [
            "|",
            ("invoicing_mode_weekly_last_execution", "<", today),
            ("invoicing_mode_weekly_last_execution", "=", False),
            ("invoicing_mode_weekly_day_todo", "=", today.weekday()),
        ]
        return self.env["res.company"].search(domain)
