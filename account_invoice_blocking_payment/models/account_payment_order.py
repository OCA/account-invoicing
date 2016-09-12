# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import UserError


class AccountPaymentOrder(models.Model):

    _inherit = 'account.payment.order'

    @api.multi
    def draft2open(self):
        for rec in self:
            for line in rec.payment_line_ids:
                if line.move_line_id.blocked:
                    raise UserError(_(
                        "At least one journal item is blocked."))
            super(AccountPaymentOrder, self).draft2open()
