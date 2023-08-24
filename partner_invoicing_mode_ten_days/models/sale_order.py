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
        (10/20/last day of month) or if that day is passed since last execution.
        """
        company_obj = self.env["res.company"]
        today = Datetime.now()
        # Get the last ten day from now (e.g.: we are the 11th of the month, get the tenth,
        # if we are the third, get the last month last day)
        last_day = today + relativedelta(day=31)
        day = today.day
        if day == last_day.day:
            pivot_date = today
        elif day >= 1 and day < 10:
            pivot_date = today + relativedelta(months=-1) + relativedelta(day=31)
        elif day >= 10 and day < 20:
            pivot_date = today + relativedelta(day=10)
        else:
            pivot_date = today + relativedelta(day=20)

        # reativedelta with day=31 returns always the last day of month
        domain = [
            "|",
            ("invoicing_mode_ten_days_last_execution", "<", pivot_date),
            ("invoicing_mode_ten_days_last_execution", "=", False),
        ]
        return company_obj.search(domain)
