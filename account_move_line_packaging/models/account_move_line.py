# Copyright 2026 ACSONE SA/NV
# Copyright 2026 BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    product_packaging_id = fields.Many2one(
        comodel_name="product.packaging",
        string="Packaging",
        check_company=True,
        compute="_compute_product_packaging_id",
        store=True,
        readonly=False,
        precompute=True,
    )
    product_packaging_qty = fields.Float(
        string="Packaging Quantity",
        digits="Product Unit of Measure",
        compute="_compute_product_packaging_qty",
        store=True,
        readonly=False,
        precompute=True,
    )
    product_packaging_domain = fields.Binary(
        compute="_compute_product_packaging_domain",
    )

    def _get_product_packaging_domain(self):
        self.ensure_one()
        return [("product_id", "=", self.product_id.id)]

    @api.depends("product_id", "move_id.move_type")
    def _compute_product_packaging_domain(self):
        for rec in self:
            rec.product_packaging_domain = rec._get_product_packaging_domain()

    @api.depends("product_id")
    def _compute_product_packaging_id(self):
        for rec in self:
            if (
                rec.product_packaging_id
                and rec.product_packaging_id.product_id != rec.product_id
            ):
                rec.product_packaging_id = False

    @api.depends("product_packaging_id")
    def _compute_product_packaging_qty(self):
        for rec in self:
            if not rec.product_packaging_id and rec.product_packaging_qty:
                rec.product_packaging_qty = 0.0

    @api.depends(
        "product_packaging_id",
        "product_packaging_qty",
        "product_uom_id",
        "display_type",
        "move_id.move_type",
    )
    def _compute_quantity(self):
        res = super()._compute_quantity()
        for rec in self:
            if (
                rec.display_type == "product"
                and rec.product_id
                and rec.product_uom_id
                and rec.product_packaging_id
                and rec.product_packaging_qty
            ):
                rec.quantity = rec._get_quantity_from_packaging()
        return res

    def _get_quantity_from_packaging(self):
        self.ensure_one()
        packaging_uom = self.product_packaging_id.product_uom_id
        qty_in_packaging_uom = (
            self.product_packaging_qty * self.product_packaging_id.qty
        )
        return packaging_uom._compute_quantity(
            qty_in_packaging_uom, self.product_uom_id
        )

    @api.constrains("product_id", "product_packaging_id")
    def _check_product_packaging_id(self):
        for line in self:
            if (
                line.product_id
                and line.product_packaging_id
                and line.product_packaging_id.product_id != line.product_id
            ):
                raise ValidationError(
                    _("The selected packaging does not belong to the selected product.")
                )
