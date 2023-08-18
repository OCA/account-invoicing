# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, models
from odoo.fields import Datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def cron_generate_ten_days_invoices(self):
        company_ids = self._get_companies_ten_days_invoicing()
        if company_ids:
            self.generate_ten_days_invoices(companies=company_ids)

    @api.model
    def generate_ten_days_invoices(self, companies=None):
        return self.generate_invoices(
            companies,
            invoicing_mode="ten_days",
            last_execution_field="invoicing_mode_ten_days_last_execution",
        )

    @api.model
    def _get_companies_ten_days_invoicing(self):
        """
        Get company ids for which today is ten days invoicing day
        (10/20/last day of month).
        """
        company_obj = self.env["res.company"]
        today = Datetime.now()
        day = today.day
        # reativedelta with day=31 returns always the last day of month
        last_day = today + relativedelta(day=31)
        if not (day in [10, 20, last_day.day]):
            return company_obj.browse()
        domain = [
            "|",
            ("invoicing_mode_ten_days_last_execution", "<", today),
            ("invoicing_mode_ten_days_last_execution", "=", False),
        ]
        return self.env["res.company"].search(domain)
