# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _convert_to_tax_base_line_dict(
        self,
        base_line,
        partner=None,
        currency=None,
        product=None,
        taxes=None,
        price_unit=None,
        quantity=None,
        discount=None,
        account=None,
        analytic_distribution=None,
        price_subtotal=None,
        is_refund=False,
        rate=None,
        handle_price_include=True,
        extra_context=None,
    ):
        """Insert the un-rounded discount value in the resulting tax computation values."""
        res = super()._convert_to_tax_base_line_dict(
            base_line,
            partner=partner,
            currency=currency,
            product=product,
            taxes=taxes,
            price_unit=price_unit,
            quantity=quantity,
            discount=discount,
            account=account,
            analytic_distribution=analytic_distribution,
            price_subtotal=price_subtotal,
            is_refund=is_refund,
            rate=rate,
            handle_price_include=handle_price_include,
            extra_context=extra_context,
        )
        if (
            base_line
            and base_line._name == "account.move.line"
            and base_line.discount_fixed
        ):
            res["discount"] = base_line._get_discount_from_fixed_discount()
        return res
