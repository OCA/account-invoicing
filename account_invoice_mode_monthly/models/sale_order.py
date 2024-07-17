# Copyright 2020 Camptocamp SA
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models
from odoo.osv.expression import OR


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def cron_generate_monthly_invoices(self):
        """Cron called daily to check if monthly invoicing needs to be done."""
        company_ids = self._company_monthly_invoicing_today()
        if company_ids:
            self.generate_monthly_invoices(company_ids)

    def generate_monthly_invoices(self, company_ids):
        return self.generate_invoices_by_invoice_mode(
            company_ids,
            "monthly",
            self._get_groupby_fields_for_monthly_invoicing(),
            "invoicing_mode_monthly_last_execution",
        )

    @api.model
    def _get_groupby_fields_for_monthly_invoicing(self):
        """Returns the sale order fields used to group them into jobs."""
        return ["partner_invoice_id", "payment_term_id"]

    @api.model
    def _company_monthly_invoicing_today(self):
        """Get company ids for which today is monthly invoicing day."""
        today = datetime.now()
        first_day_this_month = today.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        first_day_last_month = first_day_this_month - relativedelta(months=1)
        last_day_of_this_month = (today + relativedelta(day=31)).day
        # Last month still not executed, it needs to be done
        domain_last_month = [
            ("invoicing_mode_monthly_last_execution", "<", first_day_last_month),
        ]
        # Invoicing day is today or in the past and invoicing not yet done
        domain_this_month = [
            "|",
            ("invoicing_mode_monthly_last_execution", "<", first_day_this_month),
            ("invoicing_mode_monthly_last_execution", "=", False),
            ("invoicing_mode_monthly_day_todo", "<=", today.day),
        ]
        # Make sure non exisiting days are done at the end of the month
        domain_last_day_of_month = [
            "|",
            ("invoicing_mode_monthly_last_execution", "<", first_day_this_month),
            ("invoicing_mode_monthly_last_execution", "=", False),
            ("invoicing_mode_monthly_day_todo", ">", today.day),
        ]
        if today.day == last_day_of_this_month:
            domain = OR(
                [domain_last_month, domain_this_month, domain_last_day_of_month]
            )
        else:
            domain = OR([domain_last_month, domain_this_month])

        return self.env["res.company"].search(domain)
