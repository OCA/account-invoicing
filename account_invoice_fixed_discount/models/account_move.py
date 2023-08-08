# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)


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
    
    @api.model
    def create(self, vals):
        res = super().create(vals)
        if any([move_line.discount_fixed for move_line in res.invoice_line_ids]):
            res.with_context(check_move_validity=False)._recompute_tax_lines()
            res.with_context(check_move_validity=False)._onchange_invoice_line_ids()
        return res

    @api.model
    def create(self, vals):
        has_fixed_discount = any(
            [
                move_line[2].get("discount_fixed", False)
                for move_line in vals.get("invoice_line_ids", [])
            ]
        )

        res = super().create(vals)
        if res.move_type != "entry" and has_fixed_discount:
            _logger.debug("Force tax recomputation because of fixed discount")
            res.with_context(check_move_validity=False)._recompute_tax_lines()
            res.with_context(check_move_validity=False)._onchange_invoice_line_ids()
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
        prec = self.company_currency_id.decimal_places
        if not float_is_zero(self.discount_fixed, precision_digits=prec):
            if float_compare(price_unit, 0.00, precision_digits=prec) == 1:
                discount = ((self.discount_fixed) / price_unit) * 100 or 0.00
            elif float_is_zero(price_unit, precision_digits=prec):
                price_unit = abs(self.discount_fixed)
                discount = 0.00
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
        prec = self.company_currency_id.decimal_places
        if not float_is_zero(self.discount_fixed, precision_digits=prec):
            if float_compare(self.price_unit, 0.00, precision_digits=prec) == 1:
                discount = ((self.discount_fixed) / self.price_unit) * 100 or 0.00
            elif float_is_zero(self.price_unit, precision_digits=prec):
                self.price_unit = abs(self.discount_fixed)
                self.discount_fixed = 0.00
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
                    {
                        "discount_fixed": vals.get("discount_fixed"),
                        "discount": 0.00,
                        "price_unit": vals.get("price_unit"),
                    }
                )
                fixed_discount = vals.get("discount_fixed")
                price_unit = vals.get("price_unit")
                if price_unit != 0:
                    fixed_discount = (
                        vals.get("discount_fixed") / vals.get("price_unit")
                    ) * 100
                elif price_unit == 0:
                    price_unit = -fixed_discount
                    fixed_discount = 0

                vals.update(
                    {
                        "discount": fixed_discount,
                        "discount_fixed": 0.00,
                        "price_unit": price_unit,
                    }
                )
            elif vals.get("discount") or vals.get("price_unit") != vals.get(
                "price_unit"
            ):
                prev_discount.append({"discount": vals.get("discount")})
        res = super(AccountMoveLine, self).create(vals_list)
        i = 0
        for rec in res:
            if rec.discount and prev_discount:
                rec.write(prev_discount[i])
                i += 1
        return res
