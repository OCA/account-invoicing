#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"
    _partner_name_history_field_map = {
        "partner_id": "_get_partner_name_history_date",
    }

    def _get_partner_name_history_date(self):
        return (
            self.invoice_date if self.is_invoice(include_receipts=True) else self.date
        )
