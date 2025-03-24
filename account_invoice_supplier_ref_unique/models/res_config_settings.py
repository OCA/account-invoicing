# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    check_invoice_supplier_number = fields.Boolean(
        related="company_id.check_invoice_supplier_number",
        readonly=False,
    )
