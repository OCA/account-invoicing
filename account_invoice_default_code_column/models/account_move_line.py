# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    name_without_default_code = fields.Char(
        compute="_compute_name_without_default_code"
    )

    @api.depends("name", "product_id.default_code")
    def _compute_name_without_default_code(self):
        for line in self:
            line.name_without_default_code = line.name
            if line.product_id and line.product_id.default_code:
                line.name_without_default_code = line.name_without_default_code.replace(
                    f"[{line.product_id.default_code}]", ""
                ).strip()
