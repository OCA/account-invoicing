# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.order.line", "one.vat.mixin"]

    @api.constrains("taxes_id")
    def _check_only_one_vat(self):
        self._check_only_one_vat_tax_field("taxes_id")

    @api.onchange("taxes_id")
    def _onchange_only_one_vat(self):
        return self._onchange_one_vat_tax_field("taxes_id")
