# Copyright 2020 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models
from odoo.fields import Datetime
from odoo.osv.expression import AND

from odoo.addons.sale.models.sale_order import LOCKED_FIELD_STATES


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoicing_mode = fields.Selection(
        related="partner_invoice_id.invoicing_mode",
        store=True,
        index=True,
    )

    one_invoice_per_order = fields.Boolean(
        compute="_compute_one_invoice_per_order",
        readonly=False,
        store=True,
        states=LOCKED_FIELD_STATES,
        help="You can check or uncheck this if you want the periodic invoicing"
        " grouping this sale order with other ones or not.",
    )

    @api.depends("partner_invoice_id")
    def _compute_one_invoice_per_order(self):
        # We depends only on partner as if we change it, we should recompute
        # but not if the parameter on it has changed (this allows to set a different
        # value on each sale order).
        for order in self:
            order.one_invoice_per_order = order.partner_invoice_id.one_invoice_per_order

    @api.model
    def cron_generate_standard_invoices(self):
        company_ids = self._get_companies_standard_invoicing()
        if company_ids:
            self.generate_invoices(company_ids)

    @api.model
    def _get_generate_invoices_state_domain(self):
        return [("invoice_status", "=", "to invoice")]

    @api.model
    def _get_generate_invoices_domain(self, companies, invoicing_mode="standard"):
        return AND(
            [
                self._get_generate_invoices_state_domain(),
                [
                    ("invoicing_mode", "=", invoicing_mode),
                    ("company_id", "in", companies.ids),
                ],
            ]
        )

    @api.model
    def generate_invoices(
        self,
        companies=None,
        invoicing_mode="standard",
        last_execution_field="invoicing_mode_standard_last_execution",
    ):
        """
        Generate invoices in job queues depending on the invoicing
        mode (stadndard by default)
        """
        if companies is None:
            companies = self.env.company
        domain = self._get_generate_invoices_domain(
            companies=companies, invoicing_mode=invoicing_mode
        )
        saleorder_groups = self.read_group(
            domain,
            ["partner_invoice_id", "sale_ids:array_agg(id)"],
            groupby=self._get_invoice_grouping_keys(),
            lazy=False,
        )
        for saleorder_group in saleorder_groups:
            self.with_delay()._generate_invoices_by_partner(saleorder_group["sale_ids"])
        companies.write({last_execution_field: Datetime.now()})
        return saleorder_groups

    @api.model
    def _get_invoice_grouping_keys(self) -> list:
        """
        We override the standard (in sale) grouping function in order to
        add some missing keys. We remove also the partner_id key.
        """
        keys = super()._get_invoice_grouping_keys()
        if "partner_invoice_id" not in keys:
            keys.append("partner_invoice_id")
        if "payment_term_id" not in keys:
            keys.append("payment_term_id")
        # Removing unwanted keys as we group on invoiced partner
        if "partner_id" in keys:
            keys.remove("partner_id")
        return keys

    def _get_generated_invoices(self, partition):
        """
        Hook to get the generated invoices as in some extended modules,
        those invoices should not be validated yet.
        """
        return self._create_invoices(grouped=partition, final=True)

    def _generate_invoices_by_partner(self, saleorder_ids):
        """Generate invoices for a group of sale order belonging to a customer."""
        today = fields.Date.context_today(self)
        sales = (
            self.browse(saleorder_ids)
            .exists()
            .filtered_domain(self._get_generate_invoices_state_domain())
        )
        if not sales:
            return "No sale order found to invoice ?"
        # Create invoices using grouping when needed, so partition sales
        invoice_ids = set()
        for partition, sales in sales.partition(
            lambda sale: sale.one_invoice_per_order
        ).items():
            invoices = sales._get_generated_invoices(partition=partition)
            # Update invoices date to be sure no long validation (jobs) put
            # the further day date on invoices.
            invoices.write({"invoice_date": today})
            # Update each partner next invoice date
            sales.partner_invoice_id._update_next_invoice_date()
            invoice_ids.update(invoices.ids)
            for invoice in invoices:
                invoice.with_delay()._validate_invoice()
        return self.env["account.move"].browse(invoice_ids)

    @api.model
    def _get_companies_standard_invoicing(self):
        return self.env["res.company"].search([])
