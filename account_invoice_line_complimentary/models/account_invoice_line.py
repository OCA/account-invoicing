#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceLine (models.Model):
    _inherit = 'account.invoice.line'

    is_complimentary = fields.Boolean(
        string="Complimentary",
    )
