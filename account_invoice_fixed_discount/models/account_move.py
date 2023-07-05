# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _recompute_tax_lines(self, **kwargs):
        # If another module of this repo inherited this function do not execute
        # following code in order to avoid conflict
        if self.env.context.get("avoid_inherit", False) or not any(
            line.discount_fixed for line in self.line_ids
        ):
            return super(AccountMove, self)._recompute_tax_lines(**kwargs)
        old_values_by_line_id = {}
        for line in self.line_ids:
            old_values_by_line_id[line.id] = {"price_unit": line.price_unit}
            price_unit = line.price_unit - line.discount_fixed
            line.update({"price_unit": price_unit})
        res = super(
            AccountMove, self.with_context(avoid_inherit=True)
        )._recompute_tax_lines(**kwargs)
        for line in self.line_ids:
            if line.id not in old_values_by_line_id:
                continue
            line.update(old_values_by_line_id[line.id])
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits="Product Price",
        default=0.00,
        help="Fixed amount discount.",
    )

    @api.onchange("discount")
    def _onchange_discount(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange("discount_fixed")
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.constrains("discount", "discount_fixed")
    def _check_only_one_discount(self):
        for rec in self:
            for line in rec:
                if line.discount and line.discount_fixed:
                    raise ValidationError(
                        _("You can only set one type of discount per line.")
                    )

    @api.onchange("quantity", "discount", "price_unit", "tax_ids", "discount_fixed")
    def _onchange_price_subtotal(self):
        return super(AccountMoveLine, self)._onchange_price_subtotal()

    @api.model
    def _get_price_total_and_subtotal_model(
        self,
        price_unit,
        quantity,
        discount,
        currency,
        product,
        partner,
        taxes,
        move_type,
    ):
        if self.discount_fixed != 0:
            discount = ((self.discount_fixed) / price_unit) * 100 or 0.00
        return super(AccountMoveLine, self)._get_price_total_and_subtotal_model(
            price_unit, quantity, discount, currency, product, partner, taxes, move_type
        )

    @api.model
    def _get_fields_onchange_balance_model(
        self,
        quantity,
        discount,
        amount_currency,
        move_type,
        currency,
        taxes,
        price_subtotal,
        force_computation=False,
    ):
        if self.discount_fixed != 0:
            discount = ((self.discount_fixed) / self.price_unit) * 100 or 0.00
        return super(AccountMoveLine, self)._get_fields_onchange_balance_model(
            quantity,
            discount,
            amount_currency,
            move_type,
            currency,
            taxes,
            price_subtotal,
            force_computation=force_computation,
        )

    @api.model_create_multi
    def create(self, vals_list):
        prev_discount = []
        for vals in vals_list:
            if vals.get("discount_fixed"):
                prev_discount.append(
                    {"discount_fixed": vals.get("discount_fixed"), "discount": 0.00}
                )
                fixed_discount = (
                    vals.get("discount_fixed") / vals.get("price_unit")
                ) * 100
                vals.update({"discount": fixed_discount, "discount_fixed": 0.00})
            elif vals.get("discount"):
                prev_discount.append({"discount": vals.get("discount")})
        res = super(AccountMoveLine, self).create(vals_list)
        i = 0
        for rec in res:
            if rec.discount and prev_discount:
                rec.write(prev_discount[i])
                i += 1
        return res
