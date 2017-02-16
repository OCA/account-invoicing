# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
#           <contact@eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase
from openerp import fields


class PurchaseStockRefundPickingCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Add some defaults to let the test run without an accounts chart."""
        super(PurchaseStockRefundPickingCase, cls).setUpClass()
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
            "default_code": "tpr1"
        })
        cls.product.property_account_expense_id = cls.account

    def test_purchase_stock_return_1(self):
        """Test a PO with a product invoiced on received quantities.

        Receive and invoice the PO, then do a return of the picking.
        Check that the invoicing status of the purchase, and quantities
        received and billed are correct throughout the process.
        """
        # intial po
        po_vals = {
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_qty': 5.0,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price,
                'date_planned': fields.Datetime.now()})]
        }
        po = self.env['purchase.order'].create(po_vals)

        # confirm our standard po, check the picking
        po.button_confirm()
        self.assertTrue(po.picking_ids,
                        'Purchase Stock: no picking created '
                        'for invoice on receipt stockable products')

        # invoice in on receipt, nothing should be invoiced
        self.assertEqual(po.invoice_status, 'to invoice',
                         ('Purchase Stock: po invoice_status should be '
                          '"To invoice" instead of "%s".') %
                         po.invoice_status)

        # Check quantity invoiced
        inv_qty = sum(pol.qty_invoiced for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity invoiced is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity received
        rec_qty = sum(pol.qty_received for pol in po.order_line)
        self.assertEqual(rec_qty, 0.0, ('Quantity received is %s. Should be '
                                        '0.0.') % rec_qty)
        # Check quantity returned
        rec_qty = sum(pol.qty_returned for pol in po.order_line)
        self.assertEqual(rec_qty, 0.0, ('Quantity returned is %s. Should be '
                                        '0.0.') % rec_qty)

        # receive completely
        pick = po.picking_ids
        pick.force_assign()
        pick.pack_operation_product_ids.write({'qty_done': 5})
        pick.do_new_transfer()

        # Check quantity received
        rec_qty = sum(pol.qty_received for pol in po.order_line)
        self.assertEqual(rec_qty, 5.0, ('Purchase Stock: received quantity '
                                        'should be 5.0 instead of %s '
                                        'after complete receipt') % rec_qty)

        # Check quantity returned
        rec_qty = sum(pol.qty_returned for pol in po.order_line)
        self.assertEqual(rec_qty, 0.0, ('Purchase Stock: returned quantity '
                                        'should be 0.0 instead of %s '
                                        'after complete receipt') % rec_qty)
        # Check quantity to invoice
        inv_qty = sum(pol.qty_to_invoice for pol in po.order_line)
        self.assertEqual(inv_qty, 5.0, ('Quantity to invoice is %s. Should '
                                        'be 5.0.') % inv_qty)

        # Check quantity invoiced
        inv_qty = sum(pol.qty_invoiced for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity invoiced is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity to refund
        inv_qty = sum(pol.qty_to_refund for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to refund is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity refunded
        inv_qty = sum(pol.qty_refunded for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity refunded is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check invoice
        self.assertEqual(po.invoice_status, 'to invoice',
                         ('Purchase Stock: po invoice_status should be '
                          '"to invoice" instead of "%s" before '
                          'invoicing') % po.invoice_status)

        inv_1 = self.env['account.invoice'].with_context(
            type='in_invoice').create({
                'partner_id': self.partner.id,
                'purchase_id': po.id,
                'account_id': self.partner.property_account_payable_id.id
            })
        inv_1.purchase_order_change()

        # Check quantity to invoice
        inv_qty = sum(pol.qty_to_invoice for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to invoice is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity invoiced
        inv_qty = sum(pol.qty_invoiced for pol in po.order_line)
        self.assertEqual(inv_qty, 5.0, ('Quantity invoiced is %s. Should '
                                        'be 5.0.') % inv_qty)

        # Check quantity to refund
        inv_qty = sum(pol.qty_to_refund for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to refund is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity refunded
        inv_qty = sum(pol.qty_refunded for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity refunded is %s. Should '
                                        'be 0.0.') % inv_qty)

        self.assertEqual(
            po.invoice_status,
            'invoiced',
            ('Purchase Stock: po invoice_status should be "invoiced" instead '
             'of '
             '"%s" after invoicing') % po.invoice_status)

        self.assertEqual(
            po.amount_untaxed,
            inv_1.amount_untaxed_signed,
            'Purchase Stock: amount in PO and invoice should be the same')
        inv_1.signal_workflow('invoice_open')

        # Return some items, after PO was invoiced
        return_wizard = self.env["stock.return.picking"].with_context(
            active_id=pick.id).create({})
        return_wizard.product_return_moves.write({
            "quantity": 2,
        })
        return_pick = pick.browse(return_wizard.create_returns()["res_id"])
        return_pick.force_assign()
        return_pick.pack_operation_product_ids.write({'qty_done': 2})
        return_pick.do_new_transfer()

        # Check quantity returned
        rec_qty = sum(pol.qty_returned for pol in po.order_line)
        self.assertEqual(rec_qty, 2.0, ('Purchase Stock: quantity returned'
                                        'should be 2.0 instead of %s '
                                        'after complete return') % rec_qty)

        # Check quantity received
        rec_qty = sum(pol.qty_received for pol in po.order_line)
        self.assertEqual(rec_qty, 5.0, ('Purchase Stock: received quantity '
                                        'should be 5.0 instead of %s '
                                        'after complete receipt') % rec_qty)

        # Check quantity to invoice
        inv_qty = sum(pol.qty_to_invoice for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to invoice is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity invoiced
        inv_qty = sum(pol.qty_invoiced for pol in po.order_line)
        self.assertEqual(inv_qty, 5.0, ('Quantity invoiced is %s. Should '
                                        'be 5.0.') % inv_qty)

        # Check quantity to refund
        inv_qty = sum(pol.qty_to_refund for pol in po.order_line)
        self.assertEqual(inv_qty, 2.0, ('Quantity to refund is %s. Should '
                                        'be 2.0.') % inv_qty)

        # Check quantity refunded
        inv_qty = sum(pol.qty_refunded for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity refunded is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check invoice status
        self.assertEqual(
            po.invoice_status,
            'to invoice',
            ('Purchase Stock: po invoice_status should be "to invoice" '
             'instead of "%s"') % po.invoice_status)

        inv_2 = self.env['account.invoice'].with_context(
            type='in_refund').create(
            {'partner_id': self.partner.id,
             'purchase_id': po.id,
             'account_id': self.partner.property_account_payable_id.id
             })
        inv_2.purchase_order_change()

        # Check quantity to invoice
        inv_qty = sum(pol.qty_to_invoice for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to invoice is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity invoiced
        inv_qty = sum(pol.qty_invoiced for pol in po.order_line)
        self.assertEqual(inv_qty, 5.0, ('Quantity invoiced is %s. Should '
                                        'be 5.0.') % inv_qty)

        # Check quantity to refund
        inv_qty = sum(pol.qty_to_refund for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to refund is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity refunded
        inv_qty = sum(pol.qty_refunded for pol in po.order_line)
        self.assertEqual(inv_qty, 2.0, ('Quantity refunded is %s. Should '
                                        'be 2.0.') % inv_qty)

        # Check invoice status
        self.assertEqual(po.invoice_status, 'invoiced',
                         'Purchase Stock: po invoice_status should be '
                         '"invoiced" instead of "%s".' % po.invoice_status)

        self.assertEqual(
            inv_2.amount_untaxed_signed,
            inv_1.amount_untaxed_signed / 5 * -2)

        inv_2.signal_workflow('invoice_open')

    def test_purchase_stock_return_2(self):
        """Test a PO with a product invoiced on received quantities.

        Receive the PO, then do a partial return of the picking.
        Create a new invoice to get the bill for the remaining qty.
        Check that the invoicing status of the purchase, and quantities
        received and billed are correct throughout the process.
        """
        # intial po
        po_vals = {
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_qty': 5.0,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price,
                'date_planned': fields.Datetime.now()})]
        }
        po = self.env['purchase.order'].create(po_vals)

        # confirm our standard po, check the picking
        po.button_confirm()
        self.assertTrue(po.picking_ids,
                        'Purchase Stock: no picking created '
                        'for invoice on receipt stockable products')

        # invoice in on receipt, nothing should be invoiced
        self.assertEqual(po.invoice_status, 'to invoice',
                         ('Purchase Stock: po invoice_status should be '
                          '"To Invoice" instead of "%s".') %
                         po.invoice_status)

        # Check quantity returned
        rec_qty = sum(pol.qty_returned for pol in po.order_line)
        self.assertEqual(rec_qty, 0.0, ('Quantity returned'
                                        'should be 0.0 instead of %s') %
                         rec_qty)

        # Check quantity received
        rec_qty = sum(pol.qty_received for pol in po.order_line)
        self.assertEqual(rec_qty, 0.0, ('Received quantity '
                                        'should be 0.0 instead of %s') %
                         rec_qty)

        # Check quantity to invoice
        inv_qty = sum(pol.qty_to_invoice for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to invoice is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity invoiced
        inv_qty = sum(pol.qty_invoiced for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity invoiced is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity to refund
        inv_qty = sum(pol.qty_to_refund for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to refund is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity refunded
        inv_qty = sum(pol.qty_refunded for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity refunded is %s. Should '
                                        'be 0.0.') % inv_qty)

        # receive completely
        pick = po.picking_ids
        pick.force_assign()
        pick.pack_operation_product_ids.write({'qty_done': 5})
        pick.do_new_transfer()

        # Check quantity received
        rec_qty = sum(pol.qty_received for pol in po.order_line)
        self.assertEqual(rec_qty, 5.0, ('Received quantity '
                                        'should be 5.0 instead of %s') %
                         rec_qty)

        # Check quantity returned
        rec_qty = sum(pol.qty_returned for pol in po.order_line)
        self.assertEqual(rec_qty, 0.0, ('Quantity returned'
                                        'should be 0.0 instead of %s') %
                         rec_qty)

        # Check quantity to invoice
        inv_qty = sum(pol.qty_to_invoice for pol in po.order_line)
        self.assertEqual(inv_qty, 5.0, ('Quantity to invoice is %s. Should '
                                        'be 5.0.') % inv_qty)

        # Check quantity invoiced
        inv_qty = sum(pol.qty_invoiced for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity invoiced is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity to refund
        inv_qty = sum(pol.qty_to_refund for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to refund is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity refunded
        inv_qty = sum(pol.qty_refunded for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity refunded is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check invoice
        self.assertEqual(po.invoice_status, 'to invoice',
                         ('Purchase Stock: po invoice_status should be '
                          '"to invoice" instead of "%s" before '
                          'invoicing') % po.invoice_status)

        # Return some items
        return_wizard = self.env["stock.return.picking"].with_context(
            active_id=pick.id).create({})
        return_wizard.product_return_moves.write({
            "quantity": 2
        })
        return_pick = pick.browse(return_wizard.create_returns()["res_id"])
        return_pick.force_assign()
        return_pick.pack_operation_product_ids.write({'qty_done': 2})
        return_pick.do_new_transfer()

        # Check quantity received
        rec_qty = sum(pol.qty_received for pol in po.order_line)
        self.assertEqual(rec_qty, 5.0, ('Received quantity '
                                        'should be 5.0 instead of %s') %
                         rec_qty)

        # Check quantity returned
        rec_qty = sum(pol.qty_returned for pol in po.order_line)
        self.assertEqual(rec_qty, 2.0, ('Quantity returned'
                                        'should be 2.0 instead of %s') %
                         rec_qty)

        # Check quantity to invoice
        inv_qty = sum(pol.qty_to_invoice for pol in po.order_line)
        self.assertEqual(inv_qty, 3.0, ('Quantity to invoice is %s. Should '
                                        'be 3.0.') % inv_qty)

        # Check quantity invoiced
        inv_qty = sum(pol.qty_invoiced for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity invoiced is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity to refund
        inv_qty = sum(pol.qty_to_refund for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to refund is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity refunded
        inv_qty = sum(pol.qty_refunded for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity refunded is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check invoice status
        self.assertEqual(
            po.invoice_status,
            'to invoice',
            ('Purchase Stock: po invoice_status should be "to invoice" '
             'instead of "%s" before invoicing the '
             'return') % po.invoice_status)

        # Create the invoice
        inv_1 = self.env['account.invoice'].with_context(
            type='in_invoice').create({
                'partner_id': self.partner.id,
                'purchase_id': po.id,
                'account_id': self.partner.property_account_payable_id.id,
            })
        inv_1.purchase_order_change()

        # Check quantity to invoice
        inv_qty = sum(pol.qty_to_invoice for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to invoice is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity invoiced
        inv_qty = sum(pol.qty_invoiced for pol in po.order_line)
        self.assertEqual(inv_qty, 3.0, ('Quantity invoiced is %s. Should '
                                        'be 3.0.') % inv_qty)

        # Check quantity to refund
        inv_qty = sum(pol.qty_to_refund for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity to refund is %s. Should '
                                        'be 0.0.') % inv_qty)

        # Check quantity refunded
        inv_qty = sum(pol.qty_refunded for pol in po.order_line)
        self.assertEqual(inv_qty, 0.0, ('Quantity refunded is %s. Should '
                                        'be 0.0.') % inv_qty)

        self.assertEqual(
            po.invoice_status,
            'invoiced',
            ('Purchase Stock: po invoice_status should be "invoiced" instead '
             'of '
             '"%s" after invoicing') % po.invoice_status)

        self.assertEqual(
            po.amount_untaxed * 3/5,
            inv_1.amount_untaxed_signed,
            'Purchase Stock: amount invoiced should be 3/5 of the amount '
            'ordered')
        inv_1.signal_workflow('invoice_open')
