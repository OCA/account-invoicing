# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from openerp.tools.float_utils import float_compare


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    check_total = fields.Monetary(
        string='Verification Total',
        readonly=True,
        states={'draft': [('readonly', False)]})

    @api.multi
    def action_move_create(self):
        for inv in self:
            if inv.type in ('in_invoice', 'in_refund') and\
                float_compare(
                    inv.check_total,
                    inv.amount_total,
                    precision_rounding=inv.currency_id.rounding) != 0:
                raise UserError(_(
                    'Please verify the price of the invoice!\n\
                    The encoded total does not match the computed total.'))
        return super(AccountInvoice, self).action_move_create()
