# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    is_advance_account = fields.Boolean(
        string="Is Advance Account",
        help="Check this box if this account is used for advance payment compensation",
    )
