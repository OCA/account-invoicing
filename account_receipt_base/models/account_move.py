# Copyright 2023 Simone Rubino - TAKOBI
# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def get_receipt_types(self):
        return ["out_receipt", "in_receipt"]

    def is_receipt(self):
        return self.move_type in self.get_receipt_types()
