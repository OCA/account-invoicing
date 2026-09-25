# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    is_advance = fields.Boolean(
        string="Advance",
        help="Create a sale advance invoice for this payment term line.",
    )
