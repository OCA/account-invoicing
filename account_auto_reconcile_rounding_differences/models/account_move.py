# -*- coding: utf-8 -*-
# Copyright 2019, Wolfgang Pichler, Callino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        res = super(AccountMoveLine, self).reconcile(writeoff_acc_id, writeoff_journal_id)
        # find payment move lines
        remaining_moves = self.filtered(lambda m: remaining_moves.company_id.rounding_diff_amount >= abs(m.amount_residual) > 0.0 and not m.payment_id)
        if remaining_moves:
            # Do create rounding difference account entrie
            writeoff_acc_id = remaining_moves.company_id.rounding_diff_account_id
            writeoff_journal_id = remaining_moves.company_id.rounding_diff_journal_id
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff(writeoff_vals)
            #add writeoff line to reconcile algo and finish the reconciliation
            (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
            return True
        return res
