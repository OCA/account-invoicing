# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    account_invoice_check_total_exempt = fields.Boolean(
        "Exempt from verification total check",
        help="When this is checked, invoices with this journal will not force "
        "filling in the verification total. This is useful ie for the expense journal",
    )
