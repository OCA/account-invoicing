# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import api, fields, models


class ProductNameVisibilityMixin(models.AbstractModel):
    """Models inheriting this mixin must define the name and label
    fields. The `label` field must be computed using _compute_label."""

    _name = "product.name.visibility.mixin"
    _description = "Product name visibility mixin"

    hide_product_name = fields.Boolean(
        compute="_compute_hide_product_name", store=True, readonly=False
    )

    @api.depends("product_id", "product_id.hide_product_name")
    def _compute_hide_product_name(self):
        self.hide_product_name = False
        checked = self.filtered_domain([("product_id.hide_product_name", "=", True)])
        if checked:
            checked.hide_product_name = True

    @api.depends("hide_product_name")
    def _compute_label(self):
        checked = self.filtered("hide_product_name")
        self -= checked
        res = super()._compute_label()
        for record in checked:
            record.label = record.name
        return res
