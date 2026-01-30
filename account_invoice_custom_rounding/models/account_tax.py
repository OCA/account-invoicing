# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        res = super()._prepare_base_line_for_taxes_computation(record, **kwargs)
        tax_calculation = self._get_base_line_field_value_from_record(
            record, "tax_calculation_rounding_method", kwargs, "round_globally"
        )
        res.update(
            {
                "tax_calculation_rounding_method": tax_calculation,
            }
        )
        return res

    @api.model
    def _add_tax_details_in_base_line(self, base_line, company, rounding_method=None):
        tax_calculation_rounding_method = base_line.pop(
            "tax_calculation_rounding_method", None
        )
        return super()._add_tax_details_in_base_line(
            base_line,
            company,
            rounding_method=rounding_method or tax_calculation_rounding_method,
        )

    @api.model
    def _prepare_base_line_grouping_key(self, base_line):
        result = super()._prepare_base_line_grouping_key(base_line)
        result["tax_calculation_rounding_method"] = base_line.get(
            "tax_calculation_rounding_method", "round_globally"
        )
        return result
