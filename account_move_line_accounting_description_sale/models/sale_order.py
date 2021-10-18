from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        line = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        line["external_name"] = line["name"]
        product = self.env["product.template"].search([("id", "=", line["product_id"])])
        if product.accounting_description:
            line["name"] = product.accounting_description
        return line
