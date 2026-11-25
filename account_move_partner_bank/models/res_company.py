# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    bank_account_source_ids = fields.One2many(
        "bank.account.source",
        "company_id",
        string="Bank Account Sources",
    )
