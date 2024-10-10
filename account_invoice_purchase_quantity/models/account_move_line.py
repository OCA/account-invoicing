# Copyright 2016 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    purchase_line_qty_received = fields.Float(
        string="Received Qty",
        readonly=True,
        digits="Product Unit of Measure",
    )
    purchase_line_product_qty = fields.Float(
        string="Ordered Qty",
        readonly=True,
        digits="Product Unit of Measure",
    )
