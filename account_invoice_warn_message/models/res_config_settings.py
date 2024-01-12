# Copyright 2024 Solvos Consultoría Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoice_warn_message_type = fields.Selection(
        related="company_id.invoice_warn_message_type",
        string="Invoice warn message options",
        readonly=False,
        required=True,
    )
