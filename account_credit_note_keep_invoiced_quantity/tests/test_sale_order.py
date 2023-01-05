# Copyright 2023 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError

from .common import MoveReversalCase


class TestSaleOrder(MoveReversalCase):
    def test_sale_order(self):
        """Invoices are correctly reflected on the sale order

        even when linked indirectly through other invoices' reversals.
        """
        partner = self.env.ref("base.res_partner_1")
        product = self.env.ref("product.product_order_01")
        product.invoice_policy = "order"
        product2 = product.copy()
        sale = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 3,
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
                            "product_uom_qty": 2,
                            "product_uom": product.uom_id.id,
                            "price_unit": 7,
                        },
                    ),
                ],
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )

        self._confirm_sale_invoice_reverse(sale)
        invoice = sale.invoice_ids.filtered(lambda inv: inv.move_type == "out_invoice")
        refund = invoice.reversal_move_id
        self.assertEqual(len(invoice.reversal_move_id), 1)

        # Also create invoices for another sale to check those invoices don't show
        # up inadvertently in the invoices of the other sale order.
        sale2 = sale.copy()
        self._confirm_sale_invoice_reverse(sale2)
        invoice2 = sale2.invoice_ids.filtered(
            lambda inv: inv.move_type == "out_invoice"
        )

        sale.refresh()
        self.assertEqual(sale.invoice_ids, invoice + invoice.reversal_move_id)
        self.assertEqual(
            self.env["sale.order"].search(
                [("invoice_ids", "in", invoice.reversal_move_id.ids)]
            ),
            sale,
        )
        self.assertEqual(
            self.env["sale.order"].search(
                [("invoice_ids", "=", invoice.reversal_move_id.id)]
            ),
            sale,
        )
        self.assertEqual(
            self.env["sale.order"].search([("invoice_ids", "=", invoice.id)]),
            sale,
        )
        self.assertEqual(
            self.env["sale.order"].search(
                [("invoice_ids", "in", (invoice + invoice.reversal_move_id).ids)]
            ),
            sale,
        )
        self.assertEqual(
            self.env["sale.order"].search(
                [("invoice_ids", "in", (invoice + invoice2.reversal_move_id).ids)]
            ),
            sale + sale2,
        )

        # Create a reversal that does decrease invoiced quantities
        self._reverse(invoice, keep_invoiced_quantities=False)
        for line in sale.order_line:
            self.assertEqual(line.qty_to_invoice, line.product_uom_qty)
        self.assertEqual(len(invoice.reversal_move_id), 2)
        self.assertEqual(sale.invoice_ids, invoice + invoice.reversal_move_id)

        # Test recursion prevention
        invoice.reversed_entry_id = invoice2.reversal_move_id
        with self.assertRaisesRegex(ValidationError, "recursive set of reversals"):
            invoice2.reversed_entry_id = refund
