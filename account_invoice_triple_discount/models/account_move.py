# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _has_discount(self):
        self.ensure_one()
        return any(
            [
                line._compute_aggregated_discount(line.discount) > 0
                for line in self.invoice_line_ids
            ]
        )
