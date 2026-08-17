# Copyright 2026 Juan Arcos MTS <j.arcos@madetosoft.com>
# Copyright 2026 Oriol Gracia MTS <o.gracia@madetosoft.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestPurchaseOrderCreateBill(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create(
            {"name": "Test Vendor", "supplier_rank": 1}
        )
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "is_storable": True,
                "purchase_method": "receive",
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "consu",
                "is_storable": True,
                "purchase_method": "receive",
            }
        )

    def _create_po_with_two_products(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "product_qty": 10,
                            "price_unit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_b.id,
                            "product_qty": 10,
                            "price_unit": 200,
                        },
                    ),
                ],
            }
        )
        order.button_confirm()
        return order

    def test_bill_excludes_zero_qty_lines(self):
        """Lines with qty_to_invoice=0 must not appear in the bill."""
        order = self._create_po_with_two_products()
        picking = order.picking_ids
        # Receive only Product A (5 units), leave Product B at 0
        for move in picking.move_ids:
            if move.product_id == self.product_a:
                move.quantity = 5
            else:
                move.quantity = 0
        picking.button_validate()

        self.assertEqual(order.invoice_status, "to invoice")
        self.assertTrue(
            order.order_line.filtered(
                lambda line: line.product_id == self.product_a
            ).qty_to_invoice,
        )
        self.assertFalse(
            order.order_line.filtered(
                lambda line: line.product_id == self.product_b
            ).qty_to_invoice,
        )

        action = order.action_create_invoice()
        invoice = self.env["account.move"].browse(action["res_id"])

        invoice_product_ids = invoice.invoice_line_ids.mapped("product_id")
        self.assertIn(self.product_a, invoice_product_ids)
        self.assertNotIn(self.product_b, invoice_product_ids)

    def test_bill_includes_all_qty_to_invoice_lines(self):
        """When both products are received, both must appear in the bill."""
        order = self._create_po_with_two_products()
        picking = order.picking_ids
        for move in picking.move_ids:
            move.quantity = 10
        picking.button_validate()

        self.assertEqual(order.invoice_status, "to invoice")

        action = order.action_create_invoice()
        invoice = self.env["account.move"].browse(action["res_id"])

        self.assertEqual(len(invoice.invoice_line_ids), 2)
