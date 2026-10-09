# Copyright 2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    product_move_ids = fields.Many2many(
        comodel_name="account.product.move",
        string="Extra Product Moves",
        readonly=True,
        help="Sets of extra journals entries generated"
        " when invoicing products in this category.",
    )
