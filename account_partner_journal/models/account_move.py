# Copyright 2016-Today: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("partner_id")
    def _compute_journal_id(self):
        result = super()._compute_journal_id()
        for move in self.filtered(
            lambda move: "purchase" in move._get_valid_journal_types()
        ):
            move.journal_id = move._search_default_journal()
        return result

    def _search_default_journal(self):
        if self.partner_id.default_purchase_journal_id:
            return self.partner_id.default_purchase_journal_id
        return super()._search_default_journal()
