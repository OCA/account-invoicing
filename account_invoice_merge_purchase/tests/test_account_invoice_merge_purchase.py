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

from openerp.tests import common
from openerp import workflow
from datetime import datetime


def create_simple_po(self, partner, invoice_method):
    vals = {'partner_id': partner.id,
            'invoice_method': invoice_method,
            'location_id': self.ref('stock.stock_location_stock'),
            'pricelist_id': self.ref('purchase.list0'),
            'order_line': [(0, 0, {'name': 'test',
                                   'date_planned': datetime.today(),
                                   'price_unit': 10,
                                   })]
            }
    return self.po_obj.create(vals)


def pay_invoice(self, invoice):
    aml = self.aml_obj.search(
        [('account_id.type', 'in', ['payable', 'receivable']),
         ('invoice.id', '=', invoice.id)])
    ctx = self.context.copy()
    ctx.update({'active_ids': [aml.id]})
    writeoff = self.writeoff_obj.with_context(active_ids=[aml.id]).create(
        {'journal_id': self.journal01.id,
         'writeoff_acc_id': self.account01.id})
    writeoff.trans_rec_reconcile()


class TestAccountInvoiceMergePurchase(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceMergePurchase, self).setUp()
        self.partner01 = self.env.ref('base.res_partner_1')
        self.context = self.env['res.users'].context_get()
        self.po_obj = self.env['purchase.order']
        self.inv_obj = self.env['account.invoice']
        self.aml_obj = self.env['account.move.line']
        self.journal01 = self.env.ref('account.miscellaneous_journal')
        self.account01 = self.env.ref('account.a_pay')
        self.writeoff_obj = self.env['account.move.line.reconcile.writeoff']

    def test_multi_purchase_order(self):
        purchase_order01 = create_simple_po(self, self.partner01, 'order')
        # I confirm the purchase order
        workflow.trg_validate(self.uid, 'purchase.order',
                              purchase_order01.id, 'purchase_confirm',
                              self.cr)
        # I check if the purchase order is confirmed
        purchase_order01.invalidate_cache()
        self.assertEqual(purchase_order01.state, 'approved',
                         "Purchase order's state isn't correct")
        invoice_ids = purchase_order01.invoice_ids.ids
        purchase_order02 = purchase_order01.copy()
        # I confirm the purchase order
        workflow.trg_validate(self.uid, 'purchase.order',
                              purchase_order02.id, 'purchase_confirm',
                              self.cr)
        # I check if the purchase order is confirmed
        purchase_order02.invalidate_cache()
        self.assertEqual(purchase_order02.state, 'approved',
                         "Purchase order's state isn't correct")
        invoice_ids.extend(purchase_order02.invoice_ids.ids)
        invoices = self.inv_obj.browse(invoice_ids)
        invoices_info = invoices.do_merge()
        new_invoice_ids = invoices_info.keys()
        # Ensure there is only one new invoice
        self.assertEqual(len(new_invoice_ids), 1)
        # I post the created invoice
        workflow.trg_validate(self.uid, 'account.invoice', new_invoice_ids[0],
                              'invoice_open', self.cr)
        # I pay the merged invoice
        invoice = self.inv_obj.browse(new_invoice_ids)[0]
        pay_invoice(self, invoice)
        # I check if merge invoice is paid
        self.assertEqual(invoice.state, 'paid')
        purchase_order01.invalidate_cache()
        # I check if purchase order are done
        self.assertEqual(purchase_order01.state, 'done')
        self.assertEqual(purchase_order02.state, 'done')
