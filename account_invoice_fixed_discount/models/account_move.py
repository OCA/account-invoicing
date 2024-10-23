# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _recompute_tax_lines(
        self, recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None
    ):
        vals = {}
        for line in self.invoice_line_ids.filtered("discount_fixed"):
            vals[line] = {"price_unit": line.price_unit}
            price_unit = line.price_unit - line.discount_fixed
            line.update({"price_unit": price_unit})
        res = super(AccountMove, self)._recompute_tax_lines(
            recompute_tax_base_amount=recompute_tax_base_amount,
            tax_rep_lines_to_recompute=tax_rep_lines_to_recompute,
        )
        for line in vals.keys():
            line.update(vals[line])
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
        discount = self.convert_discount_fixed_to_discount(
            self.discount_fixed, self.price_unit, discount
        )
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
        discount = self.convert_discount_fixed_to_discount(
            self.discount_fixed, self.price_unit, discount
        )
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
        discount_vals_to_apply = []
        for record_index, vals in enumerate(vals_list):
            discount_fixed = vals.get("discount_fixed")
            discount = vals.get("discount")
            if discount_fixed:
                discount_vals_to_apply.append(
                    (record_index, {"discount_fixed": discount_fixed, "discount": 0.00})
                )
                discount = self.convert_discount_fixed_to_discount(
                    discount_fixed, vals.get("price_unit"), 0.00
                )
                vals.update({"discount": discount, "discount_fixed": 0.00})
            elif discount:
                discount_vals_to_apply.append((record_index, {"discount": discount}))
        records = super(AccountMoveLine, self).create(vals_list)
        for record_index, discount_vals in discount_vals_to_apply:
            records[record_index].write(discount_vals)
        return records

    @api.model
    def convert_discount_fixed_to_discount(
        self,
        discount_fixed,
        price_unit,
        default_discount,
    ):
        if not discount_fixed or not price_unit:
            return default_discount
        return (discount_fixed / price_unit) * 100
