# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = ["product.product", "product.average.price.mixin"]
    _name = "product.product"

    def _avg_price_products(self):
        return self

    @api.model
    def _cron_update_avg_prices(self):
        for company in self.env["res.company"].search([]):
            self.with_company(company).sudo()._update_invoiced_avg_prices()

    def _update_invoiced_avg_prices(self):
        """Refresh the products the active company invoiced recently."""
        date_to = fields.Date.context_today(self)
        step_days, max_steps = self._get_avg_price_window()
        groups = self.env["account.move.line"].read_group(
            [
                ("parent_state", "=", "posted"),
                ("display_type", "=", "product"),
                ("move_id.move_type", "in", ("in_invoice", "out_invoice")),
                (
                    "move_id.invoice_date",
                    ">=",
                    date_to - timedelta(days=step_days * max_steps),
                ),
                ("company_id", "=", self.env.company.id),
            ],
            ["product_id"],
            ["product_id"],
        )
        products = self.browse([g["product_id"][0] for g in groups if g["product_id"]])
        # Templates refresh their variants as well.
        products.exists().product_tmpl_id._update_avg_prices()
