# Copyright 2023 ForgeFlow S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _stock_account_anglo_saxon_reconcile_valuation(self, product=False):
        """Ignore customer invoices."""
        supplier_invoices = self.filtered(
            lambda i: i.move_type in ["in_invoice", "in_refund"]
        )
        return super(
            AccountMove, supplier_invoices
        )._stock_account_anglo_saxon_reconcile_valuation(product=product)

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        # We override the standard method to invalidate it
        super(AccountMove, self)._stock_account_prepare_anglo_saxon_out_lines_vals()
        return []
