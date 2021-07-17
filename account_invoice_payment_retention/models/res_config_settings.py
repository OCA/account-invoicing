# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_payment_retention = fields.Boolean(
        string="Enable Invoice's Retention on Payment",
        implied_group="account_invoice_payment_retention.group_payment_retention",
    )
    retention_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.retention_account_id",
        string="Retention Account",
        readonly=False,
        help="Retention account used for case payment retention",
    )
