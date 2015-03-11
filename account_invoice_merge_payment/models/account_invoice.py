# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_merge_payment,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_merge_payment is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_merge_payment is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_merge_payment.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api
from openerp.addons.account_invoice_merge.invoice import INVOICE_KEY_COLS


INVOICE_KEY_COLS.append('payment_mode_id')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_first_invoice_fields(self, invoice):
        res = super(AccountInvoice, self)._get_first_invoice_fields(invoice)
        res.update({'payment_mode_id': invoice.payment_mode_id.id})
        return res
