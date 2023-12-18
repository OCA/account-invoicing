# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.osv.expression import OR


class SaleOrder(models.Model):
    _inherit = "sale.order"

    one_invoice_per_shipping = fields.Boolean(
        compute="_compute_one_invoice_per_shipping",
        store=True,
        index=True,
    )

    @api.depends("partner_invoice_id")
    def _compute_one_invoice_per_shipping(self):
        """
        Compute this field (instead a related) to avoid computing all
        related sale orders if option changed on partner level.
        """
        for order in self:
            order.one_invoice_per_shipping = (
                order.partner_invoice_id.one_invoice_per_shipping
            )

    def _get_generate_invoices_state_domain(self):
        domain = super()._get_generate_invoices_state_domain()
        domain = OR(
            [
                domain,
                [
                    ("one_invoice_per_shipping", "=", True),
                    ("invoice_ids.state", "=", "draft"),
                ],
            ]
        )
        return domain

    def _get_generated_invoices(self, partition):
        sales_to_validate_invoices = self.filtered(
            lambda sale: sale.one_invoice_per_shipping
            and any(invoice.state == "draft" for invoice in self.invoice_ids)
        )
        sales_create_invoices = self - sales_to_validate_invoices
        if sales_create_invoices:
            invoices = super(SaleOrder, sales_create_invoices)._get_generated_invoices(
                partition
            )
        else:
            invoices = self.env["account.move"].browse()
        to_validate_invoices = sales_to_validate_invoices.mapped(
            "invoice_ids"
        ).filtered(lambda invoice: invoice.state == "draft")
        return invoices | to_validate_invoices
