# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    billing_email_template_id = fields.Many2one(
        "mail.template",
        string="Billing email template",
        domain=[("model", "=", "account.billing")],
        help="Template used for sending billing emails.",
    )
