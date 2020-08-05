# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_enable_retention = fields.Boolean(
        string="Enable Retention on Invoice",
        implied_group="account_invoice_payment_retention.group_enable_retention",
    )
    retention_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.default_account_retention_id",
        string="Account Retention",
        readonly=False,
        copy=False,
    )
    retention_percent = fields.Float(
        related="company_id.retention_percent",
        string="Retention Percent",
        readonly=False,
    )
