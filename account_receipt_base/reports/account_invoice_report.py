#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    move_type = fields.Selection(
        selection_add=[
            ("out_receipt", "Sales Receipt"),
            ("in_receipt", "Purchase Receipt"),
        ],
    )
