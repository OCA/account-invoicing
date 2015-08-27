# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_split_sale,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_split_sale is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_split_sale is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_split_sale.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
from openerp import workflow


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


class TestAccountInvoiceSplitSale(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceSplitSale, self).setUp()
        self.partner01 = self.env.ref('base.res_partner_1')
        self.context = self.env['res.users'].context_get()
        self.po_obj = self.env['sale.order']
        self.inv_obj = self.env['account.invoice']
        self.aml_obj = self.env['account.move.line']
        self.journal01 = self.env.ref('account.miscellaneous_journal')
        self.account01 = self.env.ref('account.a_pay')
        self.writeoff_obj = self.env['account.move.line.reconcile.writeoff']
        self.invoice_wiz = self.env['sale.advance.payment.inv']
        self.split_obj = self.env['account.invoice.split']

    def test_sale_order_invoice_split(self):
        sale_order_01 = self.env.ref('sale.sale_order_7').copy()
        # I confirm the sale order
        workflow.trg_validate(self.uid, 'sale.order',
                              sale_order_01.id, 'order_confirm',
                              self.cr)
        # I check if the sale order is confirmed
        sale_order_01.invalidate_cache()
        self.assertEqual(sale_order_01.state, 'manual')
        wiz_inv = self.invoice_wiz\
            .with_context(active_ids=[sale_order_01.id]).create({})
        wiz_inv.create_invoices()
        # Get the created invoice
        invoice_ids = sale_order_01.invoice_ids.ids
        invoice = self.inv_obj.browse(invoice_ids)[0]
        # Split the first line
        line_to_split = invoice.invoice_line[0]
        wiz = self.split_obj.with_context(active_ids=[invoice.id])\
            .create({})
        wiz_line = wiz.line_ids\
            .filtered(lambda r: (r.origin_invoice_line_id == line_to_split))
        quantity_to_split = 1
        wiz_line.quantity_to_split = quantity_to_split
        # Create the new invoice
        new_invoice_id = wiz._split_invoice()
        # I check if a new invoice is created
        self.assertTrue(new_invoice_id is not False)
        # I post the original invoice
        workflow.trg_validate(self.uid, 'account.invoice', invoice.id,
                              'invoice_open', self.cr)
        # I pay the the original invoice
        pay_invoice(self, invoice)
        # I check if original invoice is paid
        self.assertEqual(invoice.state, 'paid')
        # I post the created invoice
        new_invoice = self.inv_obj.browse([new_invoice_id])[0]
        workflow.trg_validate(self.uid, 'account.invoice', new_invoice.id,
                              'invoice_open', self.cr)
        # I pay the the created invoice
        pay_invoice(self, new_invoice)
        # I check if created invoice is paid
        self.assertEqual(new_invoice.state, 'paid')
        # I check that the purchase order is done
        self.assertEqual(sale_order_01.state, 'done')
