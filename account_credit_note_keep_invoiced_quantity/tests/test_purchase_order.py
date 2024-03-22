# Copyright 2023 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from .common import MoveReversalCase


class TestPurchaseOrder(MoveReversalCase):
    def test_purchase_order(self):
        """Invoices are correctly reflected on the purchase order

        even when linked indirectly through other invoices' reversals.
        """
        partner = self.env.ref("base.res_partner_1")
        product = self.env.ref("product.product_order_01")
        product.purchase_method = "purchase"
        product2 = product.copy()
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_qty": 3.0,
                            "product_uom": product.uom_id.id,
                            "price_unit": 5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product2.id,
                            "product_qty": 2.0,
                            "product_uom": product2.uom_id.id,
                            "price_unit": 7,
                        },
                    ),
                ],
            }
        )
        self._confirm_purchase_invoice_reverse(purchase)
        invoice = purchase.invoice_ids.filtered(
            lambda inv: inv.move_type == "in_invoice"
        )
        self.assertEqual(len(invoice.reversal_move_id), 1)

        # Also create invoices for another purchase to check those invoices don't show
        # up inadvertently in the invoices of the other purchase order.
        purchase2 = purchase.copy()
        self._confirm_purchase_invoice_reverse(purchase2)

        self.assertEqual(purchase.invoice_ids, invoice + invoice.reversal_move_id)

        # Create a reversal that does decrease invoiced quantities
        invoice.reversal_move_id.ref += "_1"  # Prevent duplicate vendor reference
        self._reverse(invoice, keep_invoiced_quantities=False)
        for line in purchase.order_line:
            self.assertEqual(line.qty_to_invoice, line.product_qty)
        self.assertEqual(len(invoice.reversal_move_id), 2)
        self.assertEqual(purchase.invoice_ids, invoice + invoice.reversal_move_id)
