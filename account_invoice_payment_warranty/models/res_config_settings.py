# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_payment_warranty = fields.Boolean(
        string="Enable Invoice's Warranty on Payment",
        implied_group="account_invoice_payment_warranty.group_payment_warranty",
    )
    warranty_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.warranty_account_id",
        string="Warranty Account",
        readonly=False,
        help="Warranty account used for case payment warranty",
    )
