# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models
from odoo.osv.expression import OR


class SaleOrder(models.Model):
    _inherit = "sale.order"

    one_invoice_per_picking = fields.Boolean(
        related="partner_invoice_id.one_invoice_per_picking",
        store=True,
        index=True,
    )

    def _get_generate_invoices_state_domain(self):
        domain = super()._get_generate_invoices_state_domain()
        domain = OR(
            [
                domain,
                [
                    ("one_invoice_per_picking", "=", True),
                    ("invoice_ids.state", "=", "draft"),
                ],
            ]
        )
        return domain

    def _get_generated_invoices(self, partition):
        sales_to_validate_invoices = self.filtered(
            lambda sale: sale.one_invoice_per_picking
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
