# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _prepare_base_line_tax_repartition_grouping_key(
        self, base_line, base_line_grouping_key, tax_data, tax_rep_data
    ):
        grouping_key = super()._prepare_base_line_tax_repartition_grouping_key(
            base_line, base_line_grouping_key, tax_data, tax_rep_data
        )
        if not self:
            company = self.env.company
        else:
            company = (
                self[0].company_id._accessible_branches()[:1] or self[0].company_id
            )

        if company.tax_zero_line:
            grouping_key["__keep_zero_line"] = True

        return grouping_key
