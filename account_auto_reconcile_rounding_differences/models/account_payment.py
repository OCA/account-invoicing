# -*- coding: utf-8 -*-
# Copyright 2019, Wolfgang Pichler, Callino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange('payment_difference')
    def _onchange_payment_difference(self):
        if self.invoice_ids[0].company_id.rounding_diff_amount >= abs(self.payment_difference) > 0:
            # set round diff account as writeoff account
            self.payment_difference_handling = 'reconcile'
            self.writeoff_account_id = self.invoice_ids[0].company_id.rounding_diff_account_id
        else:
            self.payment_difference_handling = 'open'
            self.writeoff_account_id = None
