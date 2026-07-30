# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ProductTemplate(models.Model):
    _inherit = ["product.template", "product.average.price.mixin"]
    _name = "product.template"

    def _avg_price_products(self):
        return self.product_variant_ids

    def _update_avg_prices(self, move_types=None):
        self.product_variant_ids._update_avg_prices(move_types=move_types)
        return super()._update_avg_prices(move_types=move_types)
