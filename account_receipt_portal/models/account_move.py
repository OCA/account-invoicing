# Copyright 2024 Sergio Zanchetta - PNLUG APS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_access_url(self):
        super(AccountMove, self)._compute_access_url()
        for move in self.filtered(lambda move: move.is_receipt()):
            move.access_url = "/my/invoices/%s" % (move.id)
