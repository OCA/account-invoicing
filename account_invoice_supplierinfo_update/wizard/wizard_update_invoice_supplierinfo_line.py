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

    product_uom_id = fields.Many2one("uom.uom", related="product_id.uom_id")

    supplierinfo_id = fields.Many2one(comodel_name="product.supplierinfo")

    current_min_quantity = fields.Float(
        string="current Min quantity", related="supplierinfo_id.min_qty", readonly=True
    )

    new_min_quantity = fields.Float(required=True)

    current_uom_id = fields.Many2one(
        string="UoM",
        comodel_name="uom.uom",
        related="supplierinfo_id.product_uom",
        readonly=True,
    )

    new_uom_id = fields.Many2one(
        comodel_name="uom.uom", string="New UoM", required=True
    )

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

    current_cost = fields.Float(
        string="Cost",
        compute="_compute_current_cost",
        digits="Product Price",
        readonly=True,
    )

    new_cost = fields.Float(
        compute="_compute_new_cost",
        digits="Product Price",
        readonly=True,
    )

    cost_variation = fields.Float(
        string="Cost Variation (%)",
        compute="_compute_cost_variation",
        digits="Discount",
    )

    def _get_fields_depend_current_cost(self):
        return ["supplierinfo_id", "product_uom_id", "current_price", "current_uom_id"]

    def _get_fields_depend_new_cost(self):
        return ["supplierinfo_id", "product_uom_id", "new_price", "new_uom_id"]

    @api.depends(lambda self: self._get_fields_depend_current_cost())
    def _compute_current_cost(self):
        self.write({"current_cost": False})
        for line in self.filtered(lambda x: x.supplierinfo_id):
            line.current_cost = line.current_uom_id._compute_price(
                line.current_price, line.product_uom_id
            )

    @api.depends(lambda self: self._get_fields_depend_new_cost())
    def _compute_new_cost(self):
        for line in self.filtered(lambda x: x.new_uom_id):
            line.new_cost = line.new_uom_id._compute_price(
                line.new_price, line.product_uom_id
            )
        for line in self.filtered(lambda x: not x.new_uom_id):
            line.new_cost = 0.0

    @api.depends("current_cost", "new_cost")
    def _compute_cost_variation(self):
        self.write({"cost_variation": False})
        for line in self.filtered("current_cost"):
            line.cost_variation = (
                100 * (line.new_cost - line.current_cost) / line.current_cost
            )

    # Custom Section
    def _prepare_supplierinfo(self):
        self.ensure_one()
        vals = {
            "product_tmpl_id": self.product_id.product_tmpl_id.id,
            "partner_id": self.wizard_id.invoice_id.supplier_partner_id.id,
            "delay": 1,
        }
        vals.update(self._prepare_supplierinfo_update())
        return vals

    def _prepare_supplierinfo_update(self):
        self.ensure_one()
        res = {
            "min_qty": self.new_min_quantity,
            "price": self.new_price,
            "currency_id": self.wizard_id.invoice_id.currency_id.id,
        }
        if self.new_uom_id:
            res["product_uom"] = self.new_uom_id.id
        return res
