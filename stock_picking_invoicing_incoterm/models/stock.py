# Copyright 2014-2020 Agile Business Group sagl
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    incoterm = fields.Many2one(
        related="sale_id.incoterm", string="Incoterm", store=True, readonly=False
    )
