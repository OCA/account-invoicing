# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    always_create_invoice_section = fields.Boolean(
        related="company_id.always_create_invoice_section",
        readonly=False,
    )
