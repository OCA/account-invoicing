# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_advance_journal = fields.Boolean(
        string="Is Compensation Advance Journal",
        help="Check this box if this journal is for compensation advances",
    )
