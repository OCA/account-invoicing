# Copyright 2020 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def is_receipt(self):
        return self.move_type in self.get_receipt_types()

    def get_receipt_types(self):
        return ["out_receipt", "in_receipt"]

    def _compute_access_url(self):
        super(AccountMove, self)._compute_access_url()
        for move in self.filtered(lambda move: move.is_receipt()):
            move.access_url = "/my/receipts/%s" % (move.id)
