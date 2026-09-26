# Copyright 2026 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def cron_generate_biweekly_invoices(self):
        """Cron called daily to check if biweekly invoicing needs to be done."""
        company_ids = self._company_biweekly_invoicing_today()
        if company_ids:
            self.generate_biweekly_invoices(company_ids)

    @api.model
    def generate_biweekly_invoices(self, companies=None):
        return self.generate_invoices(
            companies,
            invoicing_mode="biweekly",
            last_execution_field="invoicing_mode_biweekly_last_execution",
        )

    @api.model
    def _company_biweekly_invoicing_today(self):
        """Get company ids for which today is biweekly invoicing day."""
        today = datetime.now().date()
        to_invoice = self.env["res.company"]
        # Search for companies that have at least one partner in biweekly mode
        # to avoid iterating over all companies if not necessary.
        partners = self.env["res.partner"].search([("invoicing_mode", "=", "biweekly")])
        companies = partners.mapped("company_id")
        if not companies and partners:
            # If there are biweekly partners but none have a company_id,
            # we must check all companies.
            companies = self.env["res.company"].search([])

        for company in companies:
            d1 = company.invoicing_mode_biweekly_day_1
            d2 = company.invoicing_mode_biweekly_day_2
            if not d1 or not d2:
                continue

            # Calculate the last theoretical occurrence for each day
            # relativedelta(day=X) handles month-end (e.g. 31 on Feb becomes 29)
            target1 = today + relativedelta(day=d1)
            if target1 > today:
                target1 -= relativedelta(months=1)
                target1 += relativedelta(day=d1)

            target2 = today + relativedelta(day=d2)
            if target2 > today:
                target2 -= relativedelta(months=1)
                target2 += relativedelta(day=d2)

            # The latest scheduled date that should have been executed
            latest_scheduled_date = max(target1, target2)

            last_exec = company.invoicing_mode_biweekly_last_execution
            if not last_exec or last_exec.date() < latest_scheduled_date:
                to_invoice |= company

        return to_invoice
