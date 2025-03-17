# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    picking_date_field_for_invoice_date = fields.Many2one(
        related="company_id.picking_date_field_for_invoice_date",
        readonly=False,
    )
