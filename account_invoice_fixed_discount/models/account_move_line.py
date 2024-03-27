# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_fixed = fields.Monetary(
        string="Discount (Fixed)",
        default=0.0,
        currency_field="currency_id",
        help=(
            "Apply a fixed amount discount to this line. The amount is multiplied by "
            "the quantity of the product."
        ),
    )

    @api.depends("quantity", "discount", "price_unit", "tax_ids", "currency_id")
    def _compute_totals(self):
        """Adjust the computation of the price_subtotal and price_total fields to
        account for the fixed discount amount.

        By using the unrounded calculated discount value, we avoid rounding errors
        in the resulting calculated totals.
        We only need to do this for lines with a fixed discount.

        """
        done_lines = self.env["account.move.line"]
        for line in self:
            if float_is_zero(
                line.discount_fixed, precision_rounding=line.currency_id.rounding
            ):
                continue
            # Pass the actual float value of the discount to the tax computation method.
            discount = line._get_discount_from_fixed_discount()
            line_discount_price_unit = line.price_unit * (1 - (discount / 100.0))
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res["total_excluded"]
                line.price_total = taxes_res["total_included"]
            else:
                # No taxes applied on the line.
                subtotal = line.quantity * line_discount_price_unit
                line.price_total = line.price_subtotal = subtotal

            done_lines |= line

        # Compute the regular totals for regular lines.
        return super(AccountMoveLine, self - done_lines)._compute_totals()

    @api.onchange("discount_fixed")
    def _onchange_discount_fixed(self):
        """Compute the fixed discount based on the discount percentage."""
        if self.env.context.get("ignore_discount_onchange"):
            return
        self.env.context = self.with_context(ignore_discount_onchange=True).env.context
        self.discount = self._get_discount_from_fixed_discount()

    @api.onchange("discount")
    def _onchange_discount(self):
        """Compute the discount percentage based on the fixed discount.
        Ignore the onchange if the fixed discount is already set.
        """
        if self.env.context.get("ignore_discount_onchange"):
            return
        self.env.context = self.with_context(ignore_discount_onchange=True).env.context
        self.discount_fixed = 0.0

    def _get_discount_from_fixed_discount(self):
        """Calculate the discount percentage from the fixed discount amount."""
        self.ensure_one()
        currency = self.currency_id or self.company_id.currency_id
        if float_is_zero(self.discount_fixed, precision_rounding=currency.rounding):
            return 0.0
        return (
            (self.price_unit != 0)
            and ((self.discount_fixed) / self.price_unit) * 100
            or 0.00
        )
