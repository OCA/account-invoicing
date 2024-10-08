# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    external_name = fields.Char(compute="_compute_name_fields", store=True)

    @api.depends("product_id")
    def _compute_name_fields(self):
        for line in self:
            line.external_name = line.name
            if line.product_id.accounting_description:
                line.name = line.product_id.accounting_description
            else:
                line.name = line.external_name
