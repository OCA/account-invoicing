# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    fixed_amount_multiplier = fields.Selection(
        [
            ("none", "No Multiplier"),
            ("quantity", "Quantity (default)"),
            ("product_quantity", "Product Quantity"),
            ("product_weight", "Product Weight"),
        ],
        string="Multiplier",
        required=True,
        default="quantity",
        help="Controls how the quantity is used for fixed-amount taxes:\n"
        "- No Multiplier: the amount is applied once per line.\n"
        "- Quantity (default): multiplied by the line quantity, regardless "
        "of the unit of measure.\n"
        "- Product Quantity: the line quantity is converted to the product's "
        "unit of measure before multiplying.\n"
        "- Product Weight: multiplied by the total weight "
        "(product quantity × product weight).",
    )

    def _get_fixed_amount_product_quantity(self, evaluation_context):
        """Return the quantity expressed in the product's unit of measure."""
        self.ensure_one()
        quantity = evaluation_context["quantity"]
        uom_factor = evaluation_context["uom"].get("factor", 1.0) or 1.0
        product_uom_factor = evaluation_context["product"].get("uom_factor", 1.0) or 1.0
        return quantity * uom_factor / product_uom_factor

    def _get_fixed_amount_quantity(self, evaluation_context):
        """Return the quantity to multiply by the fixed tax amount.

        This hook lets downstream modules extend the fixed tax multiplier modes.

        :param dict evaluation_context: Tax computation context.
        :return: Quantity used as multiplier for the fixed tax amount.
        """
        self.ensure_one()
        if self.fixed_amount_multiplier == "none":
            return 1.0
        elif self.fixed_amount_multiplier == "product_quantity":
            return self._get_fixed_amount_product_quantity(evaluation_context)
        elif self.fixed_amount_multiplier == "product_weight":
            quantity = self._get_fixed_amount_product_quantity(evaluation_context)
            return quantity * evaluation_context["product"].get("weight", 0.0)
        return evaluation_context["quantity"]

    def _eval_tax_amount_fixed_amount(self, batch, raw_base, evaluation_context):
        if self.amount_type == "fixed" and self.fixed_amount_multiplier != "quantity":
            quantity = self._get_fixed_amount_quantity(evaluation_context)
            evaluation_context = {
                **evaluation_context,
                "quantity": quantity,
            }
        return super()._eval_tax_amount_fixed_amount(
            batch, raw_base, evaluation_context
        )

    def _eval_taxes_computation_prepare_product_fields(self):
        fields = super()._eval_taxes_computation_prepare_product_fields()
        fields.add("uom_factor")
        fields.add("weight")
        return fields

    def _eval_taxes_computation_prepare_product_uom_fields(self):
        fields = super()._eval_taxes_computation_prepare_product_uom_fields()
        fields.add("factor")
        return fields
