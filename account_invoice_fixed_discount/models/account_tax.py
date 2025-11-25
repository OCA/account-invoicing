# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        res = super()._prepare_base_line_for_taxes_computation(record, **kwargs)
        # In some cases, record can be a dict (e.g. during the creation of
        # ``account.move.line`` from a ``sale.order.line``). In that case, we cannot
        # access the ``discount_fixed`` field.
        if (
            record
            and not isinstance(record, dict)
            and record._name == "account.move.line"
            and record.discount_fixed
        ):
            res["discount"] = record._get_discount_from_fixed_discount()
        return res
