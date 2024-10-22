# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, models
from odoo.fields import Datetime
from odoo.osv import expression


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

    def _get_generate_invoices_domain(self, companies, invoicing_mode="standard"):
        today = Datetime.today()
        domain = super()._get_generate_invoices_domain(
            companies, invoicing_mode=invoicing_mode
        )
        if invoicing_mode == "ten_days":
            # We use the next_invoice_date field to generate it
            tendays_domain = [
                "|",
                ("partner_invoice_id.next_invoice_date", "=", False),
                ("partner_invoice_id.next_invoice_date", "<=", today),
            ]
            return expression.AND([domain, tendays_domain])
        return domain

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
            # reativedelta with day=31 returns always the last day of month
            pivot_date = today + relativedelta(months=-1) + relativedelta(day=31)
        elif day >= 10 and day < 20:
            pivot_date = today + relativedelta(day=10)
        else:
            pivot_date = today + relativedelta(day=20)

        # always declare pivot_date as a date object because the field
        # invoicing_mode_ten_days_last_execution is a datetime field.
        # If we don't do this and a new pivot_date is calculated,
        # for a time later than the last execution time, the domain will
        # return the same company_ids as the last execution date time since
        # in such case the last execution date time will be lesser than the pivot_date
        # ex:
        # * last execution_date_time = 2021-09-20 10:00:00
        # * _get_companies_ten_days_invoicing is called on 2021-09-21 10:30:00
        # => pivot_date = 2021-09-20 10:30:00
        # => execution_date_time < pivot_date is True
        # the call to _get_companies_ten_days_invoicing will return the same
        # company_ids as the last execution date time and the cron will run again
        # for an invoice pivot date that has already been invoiced... What we
        # want is to run the cron only once every 10 days.
        pivot_date = pivot_date.date()
        domain = [
            "|",
            ("invoicing_mode_ten_days_last_execution", "<", pivot_date),
            ("invoicing_mode_ten_days_last_execution", "=", False),
        ]
        return company_obj.search(domain)
