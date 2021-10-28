# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    external_name = fields.Char(string="External Name")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super()._onchange_product_id()
        for line in self:
            line.external_name = line.name
            if line.product_id.accounting_description:
                line.name = line.product_id.accounting_description
