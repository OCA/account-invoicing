# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    picking_date_field_for_invoice_date = fields.Many2one(
        "ir.model.fields",
        domain="[('model', '=', 'stock.picking'), ('ttype', 'in', ('date', 'datetime'))]",
    )
