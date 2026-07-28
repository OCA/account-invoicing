# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.sale.tests.common import SaleCommon


@tagged("post_install", "-at_install")
class TestInvoiceRefundLinkSale(SaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.invoice_policy = "delivery"
        cls.new_sale_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.empty_order.id,
                "product_id": cls.product.id,
                "product_uom_qty": 2.0,
                "price_unit": 100.0,
            }
        )

    def test_refund_link_from_sale_order(self):
        """Test that if there is exactly one candidate invoice,
        the refund is linked to it."""
        self.empty_order.action_confirm()
        self.new_sale_line.qty_delivered = 2.0
        self.assertEqual(self.empty_order.invoice_status, "to invoice")
        new_invoice = self.empty_order._create_invoices()
        self.assertEqual(len(new_invoice), 1)
        self.assertEqual(new_invoice.move_type, "out_invoice")
        new_invoice.action_post()
        self.assertEqual(self.empty_order.invoice_status, "invoiced")
        self.new_sale_line.qty_delivered = 0.0
        self.assertEqual(self.empty_order.invoice_status, "to invoice")
        new_refund = self.empty_order._create_invoices(final=True)
        self.assertEqual(len(new_refund), 1)
        self.assertEqual(new_refund.move_type, "out_refund")
        new_refund.action_post()
        self.assertEqual(new_refund.reversed_entry_id, new_invoice)
        self.assertEqual(len(new_invoice.refund_invoice_ids), 1)
        self.assertIn(new_refund, new_invoice.refund_invoice_ids)

    def test_refund_no_link_from_sale_order(self):
        """Test that if there are multiple candidate invoices,
        the refund is not linked to any of them."""
        self.empty_order.action_confirm()
        # Generate the first invoice for the sale order
        self.new_sale_line.qty_delivered = 1
        self.assertEqual(self.empty_order.invoice_status, "to invoice")
        new_invoice = self.empty_order._create_invoices()
        self.assertEqual(len(new_invoice), 1)
        self.assertEqual(new_invoice.move_type, "out_invoice")
        new_invoice.action_post()
        # Generate a second invoice for the same sale order
        self.new_sale_line.qty_delivered = 2
        self.assertEqual(self.empty_order.invoice_status, "to invoice")
        new_invoice2 = self.empty_order._create_invoices()
        self.assertEqual(len(new_invoice2), 1)
        self.assertEqual(new_invoice2.move_type, "out_invoice")
        new_invoice2.action_post()
        self.assertEqual(len(self.empty_order.invoice_ids), 2)
        self.assertEqual(self.empty_order.invoice_status, "invoiced")
        # Generate the refund for the sale order
        # which should not be linked to any invoice since there are multiple candidates
        self.new_sale_line.qty_delivered = 0.0
        self.assertEqual(self.empty_order.invoice_status, "to invoice")
        new_refund = self.empty_order._create_invoices(final=True)
        self.assertEqual(len(new_refund), 1)
        self.assertEqual(new_refund.move_type, "out_refund")
        new_refund.action_post()
        self.assertFalse(new_refund.reversed_entry_id)
        self.assertFalse(new_invoice.refund_invoice_ids)
        self.assertFalse(new_invoice2.refund_invoice_ids)
