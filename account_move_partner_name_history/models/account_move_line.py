#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _partner_name_history_field_map = {
        "partner_id": "_get_partner_name_history_date",
    }

    def _get_partner_name_history_date(self):
        return self.move_id._get_partner_name_history_date()
