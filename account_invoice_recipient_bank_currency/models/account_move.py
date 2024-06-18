# Copyright 2024 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("bank_partner_id", "currency_id")
    def _compute_partner_bank_id(self):
        res = super()._compute_partner_bank_id()
        for move in self:
            if move.currency_id:
                bank_ids = move.bank_partner_id.bank_ids.filtered(
                    lambda bank: (
                        not bank.company_id or bank.company_id == move.company_id
                    )
                    and (not bank.currency_id or bank.currency_id == move.currency_id)
                )
                bank_ids = bank_ids.sorted(key=lambda bank: bank.sequence)
                move.partner_bank_id = bank_ids[0] if bank_ids else move.partner_bank_id
        return res
