# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_account_retention_id = fields.Many2one(
        comodel_name="account.account", string="Account Retention",
    )
    retention_percent = fields.Float(string="Retention Percent",)
