# Copyright 2021 Camptocamp SA
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def cron_generate_weekly_invoices(self):
        """Cron called daily to check if weekly invoicing needs to be done."""
        company_ids = self._company_weekly_invoicing_today()
        if company_ids:
            self.generate_weekly_invoices(company_ids)

    @api.model
    def generate_weekly_invoices(self, company_ids):
        return self.generate_invoices_by_invoice_mode(
            company_ids,
            "weekly",
            self._get_groupby_fields_for_weekly_invoicing(),
            "invoicing_mode_weekly_last_execution",
        )

    @api.model
    def _get_groupby_fields_for_weekly_invoicing(self):
        """Returns the sale order fields used to group them into jobs."""
        return ["partner_invoice_id", "payment_term_id"]

    @api.model
    def _company_weekly_invoicing_today(self):
        """Get company ids for which today is weekly invoicing day."""
        today = datetime.now()
        domain = [
            "|",
            ("invoicing_mode_weekly_last_execution", "<", today),
            ("invoicing_mode_weekly_last_execution", "=", False),
            ("invoicing_mode_weekly_day_todo", "=", today.weekday()),
        ]
        return self.env["res.company"].search(domain)
