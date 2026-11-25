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
        readonly=False,
        help="Retention account used for case payment retention",
    )
    retention_receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.retention_receivable_account_id",
        readonly=False,
        help="Retention receivable account used for case payment retention",
    )
    retention_method = fields.Selection(
        related="company_id.retention_method",
        string="Retention Method",
        readonly=False,
        help="Method for computing the retention\n"
        "- Untaxed Amount: The retention compute from the untaxed amount\n"
        "- Total: The retention compute from the total amount",
    )
