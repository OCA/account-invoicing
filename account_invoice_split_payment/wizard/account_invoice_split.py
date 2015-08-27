# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_split_payment,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_split_payment is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_split_payment is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_split_payment.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class AccountInvoiceSplit(models.TransientModel):
    _inherit = 'account.invoice.split'

    @api.model
    def _get_invoice_values(self, invoice):
        res = super(AccountInvoiceSplit, self)._get_invoice_values(invoice)
        res['payment_mode_id'] = invoice.payment_mode_id.id
        return res
