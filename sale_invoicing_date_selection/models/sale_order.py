# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        values = super()._prepare_invoice()
        if "default_invoice_date" in self.env.context:
            values.update(
                {
                    "invoice_date": self.env.context["default_invoice_date"],
                    "date": self.env.context["default_invoice_date"],
                }
            )
        return values
