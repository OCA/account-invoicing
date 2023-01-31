# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "one.vat.mixin"]

    @api.onchange("tax_ids")
    def _onchange_only_one_vat_tax(self):
        return self._onchange_one_vat_tax_field("tax_ids")
