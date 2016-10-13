# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    blocked = fields.Boolean(store=True)

    draft_blocked = fields.Boolean(store=True)

    @api.multi
    def create_account_payment_line(self):
        """
        A blocked invoice cannot be paid
        """
        for rec in self:
            if rec.filtered(lambda inv: inv.draft_blocked or inv.blocked):
                raise UserError(_("A blocked invoice cannot be paid."))
        return super(AccountInvoice, self).create_account_payment_line()
