# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_merge_purchase,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_merge_purchase is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_merge_purchase is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_merge_purchase.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_invoice_line_key_cols(self):
        res = super(AccountInvoice, self)._get_invoice_line_key_cols()
        res.append('purchase_line_id')
        return res

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        invoices_info = super(AccountInvoice, self).do_merge(
            keep_references=keep_references, date_invoice=date_invoice)
        po_obj = self.env['purchase.order']
        invoice_line_obj = self.env['account.invoice.line']
        for new_invoice_id in invoices_info:
            todos = po_obj.search(
                [('invoice_ids', 'in', invoices_info[new_invoice_id])])
            todos.write({'invoice_ids': [(4, new_invoice_id)]})
            for org_po in todos:
                for po_line in org_po.order_line:
                    invoice_line_ids = invoice_line_obj.search(
                        [('invoice_id.state', '!=', 'cancel'),
                         ('purchase_line_id', '=', po_line.id)])
                    if invoice_line_ids.ids:
                        po_line.write(
                            {'invoice_lines': [(6, 0,
                                                invoice_line_ids.ids)]})
        return invoices_info
