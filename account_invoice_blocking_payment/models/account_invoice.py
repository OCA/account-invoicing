# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import UserError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def create_account_payment_line(self):
        """
        A blocked invoice cannot be paid
        """
        for rec in self:
            if rec.draft_blocked or rec.blocked:
                raise UserError(_(
                    "A blocked invoice cannot be paid."))
            super(AccountInvoice, self).create_account_payment_line()
