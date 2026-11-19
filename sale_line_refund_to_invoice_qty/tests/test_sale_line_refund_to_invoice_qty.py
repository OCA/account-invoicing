# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleLineRefundToInvoiceQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "consu"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    ),
                ],
            }
        )
        cls.order.action_confirm()
        cls.order.order_line[0].write({"qty_delivered": 5.0})
        cls.order._create_invoices()
        cls.invoice = cls.order.invoice_ids[0]
        cls.invoice.action_post()

    def move_reversal_wiz(self, move):
        wizard = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=[move.id])
            .create({"journal_id": move.journal_id.id})
        )
        return wizard

    def test_refund_qty_not_to_reinvoice(self):
        """
        Test that the quantities refunded are not considered as quantities to
        reinvoice in the sales order line, when the boolean is checked.
        """
        self.assertEqual(self.order.order_line[0].qty_invoiced, 5.0)
        self.assertEqual(self.order.order_line[0].qty_invoiced_posted, 5.0)
        reversal_wizard = self.move_reversal_wiz(self.invoice)
        reversal_wizard.write({"sale_qty_to_reinvoice": False})
        credit_note = self.env["account.move"].browse(
            reversal_wizard.reverse_moves()["res_id"]
        )
        for line in credit_note.line_ids:
            self.assertFalse(line.sale_qty_to_reinvoice)
        self.assertEqual(self.order.order_line[0].qty_invoiced, 5.0)
        self.assertEqual(self.order.order_line[0].qty_invoiced_posted, 5.0)
        self.assertEqual(self.order.order_line[0].qty_to_invoice, 0.0)
        self.assertEqual(self.order.order_line[0].qty_refunded_not_invoiceable, 5.0)
        # Check after posting credit note
        credit_note.action_post()
        self.assertEqual(self.order.order_line[0].qty_invoiced_posted, 5.0)

    def test_refund_qty_to_reinvoice(self):
        """
        Test that the quantities refunded are considered as quantities to
        reinvoice in the sales order line, when the boolean is left unchecked.
        """
        self.assertEqual(self.order.order_line[0].qty_invoiced, 5.0)
        self.assertEqual(self.order.order_line[0].qty_invoiced_posted, 5.0)
        reversal_wizard = self.move_reversal_wiz(self.invoice)
        credit_note = self.env["account.move"].browse(
            reversal_wizard.reverse_moves()["res_id"]
        )
        for line in credit_note.line_ids:
            self.assertTrue(line.sale_qty_to_reinvoice)
        self.assertEqual(self.order.order_line[0].qty_invoiced, 0.0)
        self.assertEqual(self.order.order_line[0].qty_invoiced_posted, 5.0)
        self.assertEqual(self.order.order_line[0].qty_to_invoice, 5.0)
        self.assertEqual(self.order.order_line[0].qty_refunded_not_invoiceable, 0.0)
        # Check after posting credit note
        credit_note.action_post()
        self.assertEqual(self.order.order_line[0].qty_invoiced_posted, 0.0)

    def test_refund_from_sale_order_to_reinvoice(self):
        """
        Test that a credit note generated from the sale order keeps its
        quantities to reinvoice: the returned quantity is invoiced back from
        the sales order and the quantity to invoice falls back to zero.
        """
        # Credit notes are not reinvoiced by default: the credit note created
        # from the sale order must still give its quantities back.
        self.env.company.reinvoice_credit_note_default = False
        product = self.env["product.product"].create(
            {
                "name": "delivered_product",
                "type": "consu",
                "invoice_policy": "delivery",
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "product_uom": product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    ),
                ],
            }
        )
        order.action_confirm()
        order_line = order.order_line[0]
        # The product is invoiced on the delivered quantities: deliver 5 and
        # invoice them.
        order_line.write({"qty_delivered": 5.0})
        order._create_invoices()
        order.invoice_ids.action_post()
        self.assertEqual(order_line.qty_invoiced, 5.0)
        # The customer returns 2 units: the delivered quantity goes back to 3.
        order_line.write({"qty_delivered": 3.0})
        self.assertEqual(order_line.qty_to_invoice, -2.0)
        credit_note = order._create_invoices(final=True)
        self.assertEqual(credit_note.move_type, "out_refund")
        for invoice_line in credit_note.invoice_line_ids:
            self.assertTrue(invoice_line.sale_qty_to_reinvoice)
        self.assertEqual(order_line.qty_to_invoice, 0.0)
        self.assertEqual(order_line.qty_refunded_not_invoiceable, 0.0)
