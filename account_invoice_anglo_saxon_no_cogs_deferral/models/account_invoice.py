# Copyright 2015-2018 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _anglo_saxon_sale_move_lines(self, i_line):
        # We override the standard method to invalidate it
        super(AccountInvoice, self)._anglo_saxon_sale_move_lines(
            i_line)
        return []
