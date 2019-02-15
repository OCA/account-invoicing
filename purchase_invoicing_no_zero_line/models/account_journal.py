# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    avoid_zero_lines = fields.Boolean(
        string="Avoid zero lines?",
        help="If this option is checked, the purchase invoices in this journal"
             " will have no lines with zero quantity"
    )
