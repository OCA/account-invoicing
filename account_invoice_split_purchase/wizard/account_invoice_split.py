# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_split_purchase,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_split_purchase is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_split_purchase is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_split_purchase.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class AccountInvoiceSplit(models.TransientModel):
    _inherit = 'account.invoice.split'

    @api.multi
    def _split_invoice(self):
        new_invoice_id = super(AccountInvoiceSplit, self)._split_invoice()
        invoice = self.env['account.invoice'].browse([new_invoice_id])[0]
        po_ids = set([])
        for line in invoice.invoice_line:
            if line.purchase_line_id.id:
                po_ids.add(line.purchase_line_id.order_id.id)
                # Link purchase line with the new invoice line
                line.purchase_line_id.invoice_lines = [(4, line.id)]
        purchase_orders = self.env['purchase.order'].browse(list(po_ids))
        # Link the new invoice with related purchase order
        purchase_orders.write({'invoice_ids': [(4, invoice.id)]})
        return new_invoice_id


class AccountInvoiceSplitLine(models.TransientModel):
    _inherit = 'account.invoice.split.line'

    @api.multi
    def _get_invoice_line_values(self):
        res = super(AccountInvoiceSplitLine, self)\
            ._get_invoice_line_values()
        res['purchase_line_id'] = \
            self.origin_invoice_line_id.purchase_line_id.id
        return res
