# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    retention_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Retention Account",
        domain=[("user_type_id.type", "=", "other")],
        help="Retention account used for case payment retention",
    )
