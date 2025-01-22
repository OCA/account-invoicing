# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    always_create_invoice_section = fields.Boolean(
        help="Defines when to create sections",
        default=False,
        string="Always create invoice section",
    )
