# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    po_invoice_auto_update_qty = fields.Boolean(
        related="company_id.po_invoice_auto_update_qty",
        string="Auto-update draft invoice quantities from PO",
        readonly=False,
        help="If enabled, lines on draft vendor bills linked to purchase order "
        "lines will have their quantities automatically updated based on the "
        "'Quantity to Invoice' field on the corresponding purchase order lines.",
    )
