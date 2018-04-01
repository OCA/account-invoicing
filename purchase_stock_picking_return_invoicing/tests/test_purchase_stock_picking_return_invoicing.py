# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo import fields


class TestPurchaseStockPickingReturnInvoicing(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Add some defaults to let the test run without an accounts chart."""
        super(TestPurchaseStockPickingReturnInvoicing, cls).setUpClass()
        cls.journal = cls.env["account.journal"].create({
            "name": "Test journal",
            "type": "purchase",
            "code": "TEST_J",
        })
        cls.account_type = cls.env["account.account.type"].create({
            "name": "Test account type",
            "type": "payable",
        })
        cls.account = cls.env["account.account"].create({
            "name": "Test account",
            "code": "TEST_A",
            "user_type_id": cls.account_type.id,
            "reconcile": True,
        })
        cls.partner = cls.env["res.partner"].create({
            "name": "Test partner",
            "supplier": True,
            "is_company": True,
        })

        cls.partner.property_account_payable_id = cls.account
        cls.product_categ = cls.env["product.category"].create({
            "name": "Test category"
        })
        cls.product = cls.env["product.product"].create({
            "name": "test product",
            "categ_id": cls.product_categ.id,
            "uom_id": cls.env.ref('product.product_uom_unit').id,
            "uom_po_id": cls.env.ref('product.product_uom_unit').id,
            "default_code": "tpr1",
        })
        cls.product.property_account_expense_id = cls.account
        cls.po = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {
                'name': cls.product.name,
                'product_id': cls.product.id,
                'product_qty': 5.0,
                'product_uom': cls.product.uom_id.id,
                'price_unit': 10,
                'date_planned': fields.Datetime.now()})]
        })
        cls.po_line = cls.po.order_line
        cls.po.button_confirm()

    def test_initial_state(self):
        self.assertEqual(self.po_line.qty_returned, 0.0)
        self.assertEqual(self.po_line.qty_received, 0.0)
        self.assertEqual(self.po_line.qty_refunded, 0.0)
        self.assertEqual(self.po_line.qty_invoiced, 0.0)
        self.assertEqual(self.po.invoice_status, 'no')

    def test_purchase_stock_return_1(self):
        """Test a PO with received, invoiced, returned and refunded qty.

        Receive and invoice the PO, then do a return of the picking.
        Check that the invoicing status of the purchase, and quantities
        received and billed are correct throughout the process.
        """
        # receive completely
        pick = self.po.picking_ids
        pick.force_assign()
        pick.pack_operation_product_ids.write({'qty_done': 5})
        pick.do_new_transfer()
        self.assertEqual(self.po_line.qty_returned, 0.0)
        self.assertEqual(self.po_line.qty_received, 5.0)
        self.assertEqual(self.po_line.qty_refunded, 0.0)
        self.assertEqual(self.po_line.qty_invoiced, 0.0)
        self.assertEqual(self.po.invoice_status, 'to invoice')
        # Make invoice
        inv_1 = self.env['account.invoice'].with_context(
            type='in_invoice',
        ).create({
            'partner_id': self.partner.id,
            'purchase_id': self.po.id,
            'account_id': self.partner.property_account_payable_id.id
        })
        inv_1.purchase_order_change()
        self.assertEqual(self.po_line.qty_returned, 0.0)
        self.assertEqual(self.po_line.qty_received, 5.0)
        self.assertEqual(self.po_line.qty_refunded, 0.0)
        self.assertEqual(self.po_line.qty_invoiced, 5.0)
        self.assertEqual(self.po.invoice_status, 'invoiced')
        self.assertAlmostEqual(inv_1.amount_untaxed_signed, 50, 2)
        # Return some items, after PO was invoiced
        return_wizard = self.env["stock.return.picking"].with_context(
            active_id=pick.id).create({})
        return_wizard.product_return_moves.write({"quantity": 2})
        return_pick = pick.browse(return_wizard.create_returns()["res_id"])
        return_pick.force_assign()
        return_pick.pack_operation_product_ids.write({'qty_done': 2})
        return_pick.do_new_transfer()
        self.assertEqual(self.po_line.qty_returned, 2.0)
        self.assertEqual(self.po_line.qty_received, 3.0)
        self.assertEqual(self.po_line.qty_refunded, 0.0)
        self.assertEqual(self.po_line.qty_invoiced, 5.0)
        self.assertEqual(self.po.invoice_status, 'to invoice')
        # Make refund
        inv_2 = self.env['account.invoice'].with_context(
            type='in_refund',
        ).create({
            'partner_id': self.partner.id,
            'purchase_id': self.po.id,
            'account_id': self.partner.property_account_payable_id.id
        })
        inv_2.purchase_order_change()
        self.assertEqual(self.po_line.qty_returned, 2.0)
        self.assertEqual(self.po_line.qty_received, 3.0)
        self.assertEqual(self.po_line.qty_refunded, 2.0)
        self.assertEqual(self.po_line.qty_invoiced, 3.0)
        self.assertEqual(self.po.invoice_status, 'invoiced')
        self.assertAlmostEqual(inv_2.amount_untaxed_signed, -20, 2)

    def test_purchase_stock_return_2(self):
        """Test a PO with received and returned qty, and invoiced after.

        Receive the PO, then do a partial return of the picking.
        Create a new invoice to get the bill for the remaining qty.
        Check that the invoicing status of the purchase, and quantities
        received and billed are correct throughout the process.
        """
        pick = self.po.picking_ids
        pick.force_assign()
        pick.pack_operation_product_ids.write({'qty_done': 5})
        pick.do_new_transfer()
        # Return some items before PO was invoiced
        return_wizard = self.env["stock.return.picking"].with_context(
            active_id=pick.id).create({})
        return_wizard.product_return_moves.write({"quantity": 2})
        return_pick = pick.browse(return_wizard.create_returns()["res_id"])
        return_pick.force_assign()
        return_pick.pack_operation_product_ids.write({'qty_done': 2})
        return_pick.do_new_transfer()
        self.assertEqual(self.po_line.qty_returned, 2.0)
        self.assertEqual(self.po_line.qty_received, 3.0)
        self.assertEqual(self.po_line.qty_refunded, 0.0)
        self.assertEqual(self.po_line.qty_invoiced, 0.0)
        self.assertEqual(self.po.invoice_status, 'to invoice')
        # Make invoice
        inv_1 = self.env['account.invoice'].with_context(
            type='in_invoice',
        ).create({
            'partner_id': self.partner.id,
            'purchase_id': self.po.id,
            'account_id': self.partner.property_account_payable_id.id
        })
        inv_1.purchase_order_change()
        self.assertEqual(self.po_line.qty_returned, 2.0)
        self.assertEqual(self.po_line.qty_received, 3.0)
        self.assertEqual(self.po_line.qty_refunded, 0.0)
        self.assertEqual(self.po_line.qty_invoiced, 3.0)
        self.assertEqual(self.po.invoice_status, 'invoiced')
        self.assertAlmostEqual(inv_1.amount_untaxed_signed, 30, 2)
