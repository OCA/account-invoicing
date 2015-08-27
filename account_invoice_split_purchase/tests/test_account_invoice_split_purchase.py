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
                                   'product_qty': 5
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


def invoice_picking(self, picking):
    wizard = self.invoice_picking_wiz.with_context(active_ids=[picking.id])\
        .create({})
    return wizard.with_context(active_ids=[picking.id]).create_invoice()


class TestAccountInvoiceSplitPurchase(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceSplitPurchase, self).setUp()
        self.partner01 = self.env.ref('base.res_partner_1')
        self.context = self.env['res.users'].context_get()
        self.po_obj = self.env['purchase.order']
        self.inv_obj = self.env['account.invoice']
        self.aml_obj = self.env['account.move.line']
        self.journal01 = self.env.ref('account.miscellaneous_journal')
        self.account01 = self.env.ref('account.a_pay')
        self.writeoff_obj = self.env['account.move.line.reconcile.writeoff']
        self.invoice_picking_wiz = self.env['stock.invoice.onshipping']
        self.split_obj = self.env['account.invoice.split']

    def test_purchase_order_invoice_split(self):
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
        invoice = self.inv_obj.browse(invoice_ids)[0]
        line_to_split = invoice.invoice_line[0]
        wiz = self.split_obj.with_context(active_ids=[invoice.id])\
            .create({})
        wiz_line = wiz.line_ids\
            .filtered(lambda r: (r.origin_invoice_line_id == line_to_split))
        quantity_to_split = 1
        wiz_line.quantity_to_split = quantity_to_split
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
        # I check that the purchase order isn't done
        self.assertNotEqual(purchase_order01.state, 'done')
        # I post the created invoice
        new_invoice = self.inv_obj.browse([new_invoice_id])[0]
        workflow.trg_validate(self.uid, 'account.invoice', new_invoice.id,
                              'invoice_open', self.cr)
        # I pay the the created invoice
        pay_invoice(self, new_invoice)
        # I check if created invoice is paid
        self.assertEqual(new_invoice.state, 'paid')
        # I check that the purchase order is done
        self.assertEqual(purchase_order01.state, 'done')

    def test_picking_purchase_order_invoice_split(self):
        purchase_order01 = self.env.ref('purchase.purchase_order_1')
        # I set the invoice method to picking
        purchase_order01.invoice_method = 'picking'
        # I confirm the purchase order
        workflow.trg_validate(self.uid, 'purchase.order',
                              purchase_order01.id, 'purchase_confirm',
                              self.cr)
        # I check if the purchase order is confirmed
        purchase_order01.invalidate_cache()
        self.assertEqual(purchase_order01.state, 'approved',
                         "Purchase order's state isn't correct")
        # I check if there is a picking
        self.assertEqual(len(purchase_order01.picking_ids.ids), 1)
        picking01 = purchase_order01.picking_ids[0]
        # I transfer the picking
        picking01.do_transfer()
        invoice_ids = invoice_picking(self, picking01)
        invoice = self.inv_obj.browse(invoice_ids)[0]
        line_to_split = invoice.invoice_line[0]
        wiz = self.split_obj.with_context(active_ids=[invoice.id])\
            .create({})
        wiz_line = wiz.line_ids\
            .filtered(lambda r: (r.origin_invoice_line_id == line_to_split))
        quantity_to_split = 1
        wiz_line.quantity_to_split = quantity_to_split
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
        # I check that the purchase order isn't done
        self.assertNotEqual(purchase_order01.state, 'done')
        # I post the created invoice
        new_invoice = self.inv_obj.browse([new_invoice_id])[0]
        workflow.trg_validate(self.uid, 'account.invoice', new_invoice.id,
                              'invoice_open', self.cr)
        # I pay the the created invoice
        pay_invoice(self, new_invoice)
        # I check if created invoice is paid
        self.assertEqual(new_invoice.state, 'paid')
        # I check that the purchase order is done
        self.assertEqual(purchase_order01.state, 'done')
