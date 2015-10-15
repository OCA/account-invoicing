# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestStockInvoicePickingIncotermSale(TransactionCase):

    def setUp(self):
        super(TestStockInvoicePickingIncotermSale, self).setUp()

        self.so = self.env['sale.order'].create({
            'partner_id': self.ref('base.res_partner_3'),
            'order_policy': 'picking',
            'incoterm': self.ref('stock.incoterm_EXW'),
        })
        self.sol = self.env['sale.order.line'].create({
            'name': '/',
            'order_id': self.so.id,
            'product_id': self.ref('product.product_product_36'),
        })

    def test_check_incoterm(self):
        self.so.action_button_confirm()
        pickings = self.so.picking_ids
        self.assertEqual(1, len(pickings))
        # check incoterm on picking
        self.assertEqual(self.ref('stock.incoterm_EXW'), pickings.incoterm.id)

        pickings.action_done()
        wizard = self.env['stock.invoice.onshipping'].with_context({
            'active_id': pickings.id,
            'active_ids': pickings.ids,
        }).create({})
        invoice_ids = wizard.create_invoice()
        invoices = self.env['account.invoice'].browse(invoice_ids)
        self.assertEqual(1, len(invoices))
        # check incoterm on invoice
        self.assertEqual(self.ref('stock.incoterm_EXW'), pickings.incoterm.id)
