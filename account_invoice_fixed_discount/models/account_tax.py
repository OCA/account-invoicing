# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.tools.float_utils import float_is_zero


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        res = super()._prepare_base_line_for_taxes_computation(record, **kwargs)

        def load(field, fallback, from_base_line=False):
            return self._get_base_line_field_value_from_record(
                record, field, kwargs, fallback, from_base_line=from_base_line
            )

        if isinstance(record, dict):
            currency = (
                load("currency_id", None)
                or load("company_currency_id", None)
                or load("company_id", self.env["res.company"]).currency_id
                or self.env["res.currency"]
            )
            discount_fixed = load("discount_fixed", 0.0)
            price_unit = load("price_unit", 0.0)

            if float_is_zero(
                discount_fixed, precision_rounding=currency.rounding
            ) or float_is_zero(price_unit, precision_rounding=currency.rounding):
                res["discount"] = 0.0
            else:
                res["discount"] = (discount_fixed / price_unit) * 100
            return res

        if record and record._name == "account.move.line" and record.discount_fixed:
            res["discount"] = record._get_discount_from_fixed_discount()
        return res
