# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _compute_account_id(self):
        res = super()._compute_account_id()
        for rec in self:
            move = rec.move_id
            if (
                rec.display_type != "payment_term"
                or not move.partner_id.parent_use_invoice_address_accounts
            ):
                continue
            partner = move.partner_id
            account = None
            if move.is_sale_document(include_receipts=True):
                account = partner.property_account_receivable_id
            elif move.is_purchase_document(include_receipts=True):
                account = partner.property_account_payable_id
            if account:
                rec.account_id = account
        return res
