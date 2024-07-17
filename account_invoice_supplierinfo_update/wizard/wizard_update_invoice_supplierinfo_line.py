# Copyright 2016 Chafique DELLI @ Akretion
# Copyright 2016-Today: GRAP (http://www.grap.coop)
# Copyright Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _name = "wizard.update.invoice.supplierinfo.line"
    _description = "Wizard Line to update supplierinfo"

    wizard_id = fields.Many2one(
        comodel_name="wizard.update.invoice.supplierinfo",
        required=True,
        ondelete="cascade",
    )

    product_id = fields.Many2one("product.product", string="Product")

    supplierinfo_id = fields.Many2one(comodel_name="product.supplierinfo")

    current_min_quantity = fields.Float(
        related="supplierinfo_id.min_qty", readonly=True
    )

    new_min_quantity = fields.Float(string="New Min Quantity", required=True)

    current_price = fields.Float(
        related="supplierinfo_id.price",
        digits="Product Price",
        readonly=True,
    )

    new_price = fields.Float(
        string="New Unit Price",
        digits="Product Price",
        required=True,
    )

    price_variation = fields.Float(
        string="Price Variation (%)",
        compute="_compute_price_variation",
        digits="Discount",
    )

    @api.depends("current_price", "new_price")
    def _compute_price_variation(self):
        self.write({"price_variation": False})
        for line in self.filtered("current_price"):
            line.price_variation = (
                100 * (line.new_price - line.current_price) / line.current_price
            )

    # Custom Section
    def _prepare_supplierinfo(self):
        self.ensure_one()
        vals = {
            "product_tmpl_id": self.product_id.product_tmpl_id.id,
            "name": self.wizard_id.invoice_id.supplier_partner_id.id,
            "delay": 1,
        }
        vals.update(self._prepare_supplierinfo_update())
        return vals

    def _prepare_supplierinfo_update(self):
        self.ensure_one()
        return {
            "min_qty": self.new_min_quantity,
            "price": self.new_price,
            "currency_id": self.wizard_id.invoice_id.currency_id.id,
        }
