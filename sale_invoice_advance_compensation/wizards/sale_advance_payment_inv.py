# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    apply_advance_compensation = fields.Boolean(
        default=True,
        help="Automatically compensate paid sale advances linked to advance "
        "payment term lines when the regular invoice is posted.",
    )

    def _create_invoices(self, sale_orders):
        if self.apply_advance_compensation:
            return super()._create_invoices(sale_orders)
        invoices = super()._create_invoices(
            sale_orders.with_context(skip_sale_advance_compensation=True)
        )
        invoices.skip_sale_advance_compensation = True
        return invoices

    def _prepare_base_downpayment_line_values(self, order):
        values = super()._prepare_base_downpayment_line_values(order)
        advance_product_id = self.env.context.get("sale_advance_product_id")
        if advance_product_id:
            values["product_id"] = advance_product_id
        return values
