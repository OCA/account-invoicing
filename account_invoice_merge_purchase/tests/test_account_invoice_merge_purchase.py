# -*- coding: utf-8 -*-
# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2009-2016 Noviat
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tests.common import SavepointCase


class TestAccountInvoiceMergePurchase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceMergePurchase, cls).setUpClass()
        cls.invoice_model = cls.env['account.invoice']
        cls.purchase_model = cls.env['purchase.order']
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })
        cls.product = cls.env['product.product'].create(
            {
                'name': 'Product test',
                'type': 'product',
                'default_code': 'PROD1',
                'uom_po_id': 1,
            }
        )

    def test_picking_multi_purchase_order(self):
        po_vals = {
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_qty': 7.0,
                    'product_uom': self.product.uom_po_id.id,
                    'price_unit': 500.0,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                })],
        }
        self.purchase_order = self.purchase_model.create(po_vals)
        # I confirm the purchase order
        self.purchase_order.button_confirm()
        self.assertEqual(self.purchase_order.state, 'purchase',
                         'Purchase: PO state should be "Purchase"')
        self.assertEqual(
            self.purchase_order.invoice_status, 'to invoice',
            'Purchase: PO invoice_status should be "Waiting Invoices"')
        # I check if there is a picking
        self.assertEqual(self.purchase_order.picking_count, 1,
                         'Purchase: one picking should be created"')
        # I receive picking order
        self.picking01 = self.purchase_order.picking_ids[0]
        self.picking01.force_assign()
        self.picking01.pack_operation_product_ids.write({'qty_done': 7.0})
        self.picking01.do_new_transfer()
        self.assertEqual(self.purchase_order.order_line.mapped('qty_received'),
                         [7.0],
                         'Purchase: all products should be received"')
        # I create invoice
        self.invoice01 = self.invoice_model.create({
            'partner_id': self.partner.id,
            'purchase_id': self.purchase_order.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        self.invoice01.purchase_order_change()

        # I create the second purchase order
        self.purchase_order02 = self.purchase_order.copy()
        # I confirm the second purchase order
        self.purchase_order02.button_confirm()
        self.assertEqual(self.purchase_order02.state, 'purchase',
                         'Purchase: PO state should be "Purchase"')
        self.assertEqual(
            self.purchase_order02.invoice_status, 'to invoice',
            'Purchase: PO invoice_status should be "Waiting Invoices"')
        # I check if there is a picking
        self.assertEqual(self.purchase_order02.picking_count, 1,
                         'Purchase: one picking should be created"')
        # I receive picking order
        self.picking02 = self.purchase_order02.picking_ids[0]
        self.picking02.force_assign()
        self.picking02.pack_operation_product_ids.write({'qty_done': 7.0})
        self.picking02.do_new_transfer()
        self.assertEqual(
            self.purchase_order02.order_line.mapped('qty_received'),
            [7.0],
            'Purchase: all products should be received"')
        # I create the second invoice
        self.invoice02 = self.invoice_model.create({
            'partner_id': self.partner.id,
            'purchase_id': self.purchase_order02.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        self.invoice02.purchase_order_change()
        invoices = self.invoice01 + self.invoice02
        invoices_info = invoices.do_merge()
        new_invoice_ids = invoices_info.keys()
        # Ensure there is only one new invoice
        self.assertEqual(len(new_invoice_ids), 1)
        # I pay the merged invoice
        invoice = self.invoice_model.browse(new_invoice_ids)[0]
        # I validate invoice by creating on
        invoice.signal_workflow('invoice_open')
        invoice.pay_and_reconcile(
            self.env['account.journal'].search([('type', '=', 'bank')],
                                               limit=1), 7000.0)
        # I check if merge invoice is paid
        self.assertEqual(invoice.state, 'paid')
