# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models
from odoo.osv.expression import OR

from odoo.addons.queue_job.job import job


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def cron_generate_monthly_invoices(self):
        """Cron called daily to check if monthly invoicing needs to be done."""
        company_ids = self._company_monthly_invoicing_today()
        if company_ids:
            self.generate_monthly_invoices(company_ids)

    @api.model
    def generate_monthly_invoices(self, companies=None):
        """Generate monthly invoices for customers who require that mode."""
        if not companies:
            companies = self.company_id
        partner_ids = self.read_group(
            [
                ("invoicing_mode", "=", "monthly"),
                ("invoice_status", "=", "to invoice"),
                ("company_id", "in", companies.ids),
            ],
            ["partner_invoice_id"],
            groupby=["partner_invoice_id"],
        )
        for partner in partner_ids:
            self.with_delay()._generate_invoices_by_partner(
                partner["partner_invoice_id"][0]
            )
        companies.write({"invoicing_mode_monthly_last_execution": datetime.now()})
        return partner_ids

    @job(default_channel="root.invoice_monthly")
    def _generate_invoices_by_partner(self, partner_id, invoicing_mode="monthly"):
        """Generate invoices for a customer sales order."""
        partner = self.env["res.partner"].browse(partner_id)
        if partner.invoicing_mode != invoicing_mode:
            return "Customer {} is not configured for monthly invoicing.".format(
                partner.name
            )
        sales = self.search(
            [
                ("invoice_status", "=", "to invoice"),
                ("partner_invoice_id", "=", partner.id),
                ("order_line.qty_to_invoice", "!=", 0),
            ]
        )
        # By default grouped by partner/currency. Refund are not generated
        invoices = sales._create_invoices(
            grouped=partner.one_invoice_per_order, final=True
        )
        for invoice in invoices:
            invoice.with_delay()._validate_invoice()
        return invoices

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
