# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    po_invoice_auto_update_qty = fields.Boolean(
        string="Auto-update draft invoice quantities from PO",
        default=False,
    )
