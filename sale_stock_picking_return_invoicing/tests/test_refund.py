# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase


class SaleStockRefundPickingCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Add some defaults to let the test run without an accounts chart."""
        super(SaleStockRefundPickingCase, cls).setUpClass()
        cls.journal = cls.env["account.journal"].create({
            "name": "Test journal",
            "type": "sale",
            "code": "TEST_J",
        })
        cls.account_type = cls.env["account.account.type"].create({
            "name": "Test account type",
            "type": "receivable",
        })
        cls.account = cls.env["account.account"].create({
            "name": "Test account",
            "code": "TEST_A",
            "user_type_id": cls.account_type.id,
            "reconcile": True,
        })
        cls.partner = cls.env.ref('base.res_partner_1')
        cls.partner.property_account_receivable_id = cls.account
        cls.product = cls.env.ref('product.product_product_6')
        cls.product.property_account_income_id = cls.account

    def test_sale_stock_return(self):
        """Test a SO with a product invoiced on delivery.

        Deliver and invoice the SO, then do a return of the picking. Check that
        a refund invoice is well generated.
        """
        # intial so
        so_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        }
        so = self.env['sale.order'].create(so_vals)

        # confirm our standard so, check the picking
        so.action_confirm()
        self.assertTrue(
            so.picking_ids,
            'Sale Stock: no picking created for "invoice on delivery" '
            'stockable products')

        # invoice in on delivery, nothing should be invoiced
        self.assertEqual(
            so.invoice_status,
            'no',
            'Sale Stock: so invoice_status should be "no" instead of "%s".' %
            so.invoice_status)

        # deliver completely
        pick = so.picking_ids
        pick.force_assign()
        pick.pack_operation_product_ids.write({'qty_done': 5})
        pick.do_new_transfer()

        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in so.order_line)
        self.assertEqual(
            del_qty,
            5.0,
            ('Sale Stock: delivered quantity should be 5.0 instead of %s '
             'after complete delivery') % del_qty)

        # Check invoice
        self.assertEqual(
            so.invoice_status,
            'to invoice',
            ('Sale Stock: so invoice_status should be "to invoice" instead of '
             '"%s" before invoicing') % so.invoice_status)
        inv_1_id = so.action_invoice_create()
        self.assertEqual(
            so.invoice_status,
            'invoiced',
            ('Sale Stock: so invoice_status should be "invoiced" instead of '
             '"%s" after invoicing') % so.invoice_status)
        self.assertEqual(
            len(inv_1_id),
            1,
            'Sale Stock: only one invoice instead of "%s" should be created' %
            len(inv_1_id))
        inv_1 = self.env['account.invoice'].browse(inv_1_id)
        self.assertEqual(
            so.amount_untaxed,
            inv_1.amount_untaxed_signed,
            'Sale Stock: amount in SO and invoice should be the same')
        inv_1.signal_workflow('invoice_open')

        # Return some items, after SO was invoiced
        return_wizard = self.env["stock.return.picking"].with_context(
            active_id=pick.id).create({})
        return_wizard.product_return_moves.write({
            "quantity": 2,
            "to_refund_so": True,
        })
        return_pick = pick.browse(return_wizard.create_returns()["res_id"])
        return_pick.force_assign()
        return_pick.pack_operation_product_ids.write({'qty_done': 2})
        return_pick.do_new_transfer()

        # Check return invoice
        self.assertEqual(
            so.invoice_status,
            'to invoice',
            ('Sale Stock: so invoice_status should be "to invoice" instead of '
             '"%s" before invoicing the return') % so.invoice_status)
        inv_2_id = so.action_invoice_create(final=True)
        self.assertEqual(
            so.invoice_status,
            'no',
            ('Sale Stock: so invoice_status should be "no" instead of '
             '"%s" after invoicing the return') % so.invoice_status)
        self.assertEqual(
            len(inv_2_id),
            1,
            'Sale Stock: only one invoice instead of "%s" should be created' %
            len(inv_2_id))
        inv_2 = self.env['account.invoice'].browse(inv_2_id)
        self.assertEqual(
            inv_2.amount_untaxed_signed,
            inv_1.amount_untaxed_signed / 5 * -2)
        inv_1.signal_workflow('invoice_open')

        # Return some items, after SO was invoiced with
        # to_refund_so value set to False
        return_wizard = self.env["stock.return.picking"].with_context(
            active_id=pick.id).create({})
        return_wizard.product_return_moves.write({
            "quantity": 2.0,
            "to_refund_so": False,
        })
        return_pick = pick.browse(return_wizard.create_returns()["res_id"])
        return_pick.force_assign()
        return_pick.pack_operation_product_ids.write({'qty_done': 2})
        return_pick.do_new_transfer()

        # Check returned quantities in sale order
        so_lines = return_pick.mapped(
            'move_lines.procurement_id.sale_line_id').filtered(
            lambda x: x.product_id.invoice_policy in ('order', 'delivery'))
        self.assertEqual(so_lines[:1].qty_returned, 4.0)

        # Check return invoice
        self.assertEqual(
            so.invoice_status,
            'no',
            ('Sale Stock: so invoice_status should be "no" instead of '
             '"%s" after invoicing the return') % so.invoice_status)

        # Update picking after it has been confirmed
        return_pick.to_refund_lines = 'no_refund_so'
        self.assertFalse(all(return_pick.mapped('move_lines.to_refund_so')))

        return_pick.to_refund_lines = 'keep_line_value'
        self.assertFalse(all(return_pick.mapped('move_lines.to_refund_so')))

        return_pick.to_refund_lines = 'to_refund_so'
        self.assertTrue(all(return_pick.mapped('move_lines.to_refund_so')))
        self.assertEqual(so.invoice_status, 'to invoice')
