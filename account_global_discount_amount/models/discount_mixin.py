# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class DiscountMixin(models.AbstractModel):
    _name = "discount.mixin"
    _description = "Discount Mixin"
    _gd_lines_field = None
    _gd_tax_field = None

    global_discount_amount = fields.Float(
        string="Global Discount Amount", tracking=True, digits="Discount"
    )
    # TODO rename to global_discount_invalid ?
    global_discount_ok = fields.Boolean(
        string="Global Discount OK",
        compute="_compute_global_discount_ok",
        store=True,
        help="The application of the global discount amount is right",
    )
    global_discount_base_on = fields.Selection(
        selection=[
            ("tax_inc", "Tax Inc"),
            ("tax_exc", "Tax Exc"),
        ],
        compute="_compute_global_discount_base_on",
        store=True,
    )

    def _compute_global_discount_base_on_depends(self):
        return [self._gd_lines_field, "global_discount_amount"]

    @api.depends(lambda self: self._compute_global_discount_base_on_depends())
    def _compute_global_discount_base_on(self):
        for record in self:
            if record.global_discount_amount:
                price_included = record[self._gd_lines_field][
                    self._gd_tax_field
                ].mapped("price_include")
                if all(price_included):
                    record.global_discount_base_on = "tax_inc"
                elif not any(price_included):
                    record.global_discount_base_on = "tax_exc"
                else:
                    # This case is too complexe so we skip it for now
                    # we should need real case before implementing something complexe
                    raise UserError(
                        _(
                            "You can not add a global discount if the taxes on lines "
                            "are a mix of included and excluded"
                        )
                    )

    def get_discount_lines(self):
        return self[self._gd_lines_field].filtered("is_discount_line")

    def _get_total_field(self):
        if self.global_discount_base_on == "tax_inc":
            return "price_total"
        else:
            return "price_subtotal"

    @api.depends(
        "global_discount_amount",
        "amount_tax",
        "amount_total",
        "global_discount_base_on",
    )
    def _compute_global_discount_ok(self):
        for record in self:
            tax2amount = record._get_tax_to_amount()
            lines = record.get_discount_lines()
            if len(tax2amount) != len(lines):
                record.global_discount_ok = False
            else:
                ok = True
                dp = self.env["decimal.precision"].precision_get("Product Price")
                for line in lines:
                    if float_compare(
                        tax2amount[line[self._gd_tax_field]],
                        -line.price_unit,
                        precision_digits=dp,
                    ):
                        ok = False
                        break
                record.global_discount_ok = ok

    @api.constrains("global_discount_amount")
    def _check_global_discount_amount(self):
        for record in self:
            if record.global_discount_amount < 0.0:
                raise UserError(_("Global Discount Amount must be a positive number !"))

    def _round_tax_to_amount(self, res):
        unrounded = res.copy()
        dp = self.env["decimal.precision"].precision_get("Product Price")
        for taxes in res:
            res[taxes] = float_round(res[taxes], precision_digits=dp)

        discount = sum(res.values())
        diff = float_compare(discount, self.global_discount_amount, dp)
        if diff:
            if diff == 1:
                # discount > self.global_discount_amount
                rounding_method = "DOWN"
            else:
                rounding_method = "UP"

            # Sort in order to start with the biggest value to reduce delta rounding
            for taxes in sorted(res, key=lambda x: res[x], reverse=True):
                discount -= res[taxes]
                res[taxes] = float_round(
                    unrounded[taxes],
                    precision_digits=dp,
                    rounding_method=rounding_method,
                )
                discount += res[taxes]
                if not float_compare(discount, self.global_discount_amount, dp):
                    break
            else:
                # This case should not occure, if it's happen
                # please open an ticket on github and ping me
                # @sebastienbeau
                raise UserError(
                    _(
                        "Fail to compute discount line due to rounding issue, "
                        "please report the issue to your integrator"
                    )
                )
        return res

    def _get_tax_to_amount(self):
        total_field = self._get_total_field()
        res = defaultdict(float)
        lines = self[self._gd_lines_field].filtered(lambda s: not s.is_discount_line)
        total = sum(lines.mapped(total_field))
        for line in lines:
            amount = line[total_field] / total * self.global_discount_amount
            if amount:
                res[line[self._gd_tax_field]] += amount
        return self._round_tax_to_amount(res)

    def _prepare_discount_line_vals(self, taxes, amount):
        discount_product = self.env.ref(
            "account_global_discount_amount.discount_product"
        )
        return {
            "product_id": discount_product.id,
            "price_unit": -1 * amount,
            "is_discount_line": True,
            self._gd_tax_field: [(6, 0, taxes.ids)],
        }

    def _add_discount_line(self):
        discount_lines = []
        for taxes, amount in self._get_tax_to_amount().items():
            discount_lines.append(
                (0, 0, self._prepare_discount_line_vals(taxes, amount))
            )
        self.with_context(skip_post_process=True).write(
            {self._gd_lines_field: discount_lines}
        )

    def _post_process_discount_line(self):
        self.get_discount_lines().unlink()
        if self.global_discount_amount:
            self._add_discount_line()

    @api.model_create_multi
    def create(self, list_vals):
        self = self.with_context(edit_discount_from_parent=True)
        records = super().create(list_vals)
        records.filtered(
            lambda s: not s.global_discount_ok
        )._post_process_discount_line()
        return records.with_context(edit_discount_from_parent=False)

    def write(self, vals):
        self = self.with_context(edit_discount_from_parent=True)
        super().write(vals)
        if not self._context.get("skip_post_process"):
            self.filtered(
                lambda s: not s.global_discount_ok
            )._post_process_discount_line()
        return True


class DiscountLineMixin(models.AbstractModel):
    _name = "discount.line.mixin"
    _description = "Discount Line Mixin"
    _gd_parent_field = None

    is_discount_line = fields.Boolean(string="Is Discount Line")

    def _post_process_discount_line(self):
        if not self._context.get("edit_discount_from_parent"):
            self[self._gd_parent_field].filtered(
                lambda s: not s.global_discount_ok
            )._post_process_discount_line()

    @api.model_create_multi
    def create(self, list_vals):
        records = super().create(list_vals)
        records._post_process_discount_line()
        return records

    def write(self, vals):
        super().write(vals)
        self._post_process_discount_line()
        return True
