# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    billing_portal_report = fields.Many2one(
        "ir.actions.report",
        domain=[("model", "=", "account.billing")],
        help="This report template will be used in the billing portal to "
        "show the billing and as the report attached to billing emails.",
    )
