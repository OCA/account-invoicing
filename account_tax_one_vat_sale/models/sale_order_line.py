# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "one.vat.mixin"]

    @api.constrains("tax_ids")
    def _check_only_one_vat(self):
        self._check_only_one_vat_tax_field("tax_ids")

    @api.onchange("tax_ids")
    def _onchange_only_one_vat(self):
        return self._onchange_one_vat_tax_field("tax_ids")
