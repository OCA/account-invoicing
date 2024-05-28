# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        line = super()._prepare_invoice_line(**optional_values)
        line["external_name"] = line["name"]
        product_id = line.get("product_id")
        if product_id:
            product = self.env["product.product"].browse(line["product_id"])
            if product.accounting_description:
                line["name"] = product.accounting_description
        return line
