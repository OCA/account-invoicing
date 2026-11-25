# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("bank_partner_id", "partner_id", "team_id")
    def _compute_partner_bank_id(self):
        return super()._compute_partner_bank_id()
