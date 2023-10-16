# Copyright 2023 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move"]

    def _get_starting_sequence(self):
        starting_sequence = super()._get_starting_sequence()

        if (
            self.journal_id.refund_sequence
            and self.journal_id.refund_code
            and starting_sequence
        ):
            starting_sequence = starting_sequence.replace(
                f"R{self.journal_id.code}", self.journal_id.refund_code
            )

        return starting_sequence
