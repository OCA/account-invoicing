# Copyright 2025 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    journal_account_utility_id = fields.Many2one(
        comodel_name="account.journal",
    )
