from odoo import Command
from odoo.tests import tagged

from odoo.addons.sale.tests.common import SaleCommon


@tagged("post_install", "-at_install")
class TestSaleInvoiceabilityOnPaymentTransaction(SaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_delivery = cls.env["product.product"].create(
            {
                "name": "Product Delivery Policy",
                "type": "consu",
                "is_storable": True,
                "invoice_policy": "delivery",
                "list_price": 100.0,
                "taxes_id": [Command.clear()],
            }
        )
        cls.provider = cls.env.ref(
            "payment.payment_provider_demo", raise_if_not_found=False
        ) or cls.env["payment.provider"].search([("code", "=", "demo")], limit=1)

    def _create_sale_order(self, qty=1):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_delivery.id,
                            "product_uom_qty": qty,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        order.action_confirm()
        return order

    def _create_done_transaction(self, order, amount=None):
        tx = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "payment_method_id": self.env.ref("payment.payment_method_unknown").id,
                "amount": amount or order.amount_total,
                "currency_id": order.currency_id.id,
                "partner_id": order.partner_id.id,
                "operation": "offline",
                "state": "done",
                "sale_order_ids": [Command.link(order.id)],
            }
        )
        return tx

    def test_fully_paid(self):
        """Fully paid order: qty_to_invoice equals ordered qty."""
        order = self._create_sale_order(qty=2)
        line = order.order_line[0]
        self.assertEqual(line.qty_to_invoice, 0.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 0.0)
        self.assertEqual(line.amount_to_invoice, 0.0)
        self.assertEqual(line.amount_invoiced, 0.0)
        self.assertEqual(line.untaxed_amount_invoiced, 0.0)
        self.assertEqual(line.invoice_status, "no")
        self._create_done_transaction(order)
        self.assertTrue(order._is_paid())
        self.assertEqual(line.qty_to_invoice, 2.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 200.0)
        self.assertEqual(line.amount_to_invoice, 200.0)
        self.assertEqual(line.amount_invoiced, 0.0)
        self.assertEqual(line.untaxed_amount_invoiced, 0.0)
        self.assertEqual(line.invoice_status, "to invoice")
        invoice = order._create_invoices()
        invoice.action_post()
        self.assertEqual(line.qty_to_invoice, 0.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 0.0)
        self.assertEqual(line.amount_to_invoice, 0.0)
        self.assertEqual(line.amount_invoiced, 200.0)
        self.assertEqual(line.untaxed_amount_invoiced, 200.0)
        self.assertEqual(line.invoice_status, "invoiced")

    def test_partial_payment(self):
        """Partially paid order: qty_to_invoice remains 0."""
        order = self._create_sale_order(qty=2)
        line = order.order_line[0]
        self._create_done_transaction(order, amount=50.0)
        self.assertFalse(order._is_paid())
        self.assertEqual(line.qty_to_invoice, 0.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 0.0)
        self.assertEqual(line.amount_to_invoice, 0.0)
        self.assertEqual(line.amount_invoiced, 0.0)
        self.assertEqual(line.untaxed_amount_invoiced, 0.0)
        self.assertEqual(line.invoice_status, "no")

    def test_no_payment(self):
        """No payment: qty_to_invoice is 0 for delivery policy."""
        order = self._create_sale_order()
        line = order.order_line[0]
        self.assertFalse(order._is_paid())
        self.assertEqual(line.qty_to_invoice, 0.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 0.0)
        self.assertEqual(line.amount_to_invoice, 0.0)
        self.assertEqual(line.amount_invoiced, 0.0)
        self.assertEqual(line.untaxed_amount_invoiced, 0.0)
        self.assertEqual(line.invoice_status, "no")

    def test_fully_paid_with_returned_full_quantity(self):
        order = self._create_sale_order(qty=2)
        line = order.order_line[0]
        self.assertEqual(line.qty_to_invoice, 0.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 0.0)
        self.assertEqual(line.amount_to_invoice, 0.0)
        self.assertEqual(line.amount_invoiced, 0.0)
        self.assertEqual(line.untaxed_amount_invoiced, 0.0)
        self.assertEqual(line.invoice_status, "no")
        self._create_done_transaction(order)
        self.assertTrue(order._is_paid())
        self.assertEqual(line.qty_to_invoice, 2.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 200.0)
        self.assertEqual(line.amount_to_invoice, 200.0)
        self.assertEqual(line.amount_invoiced, 0.0)
        self.assertEqual(line.untaxed_amount_invoiced, 0.0)
        self.assertEqual(line.invoice_status, "to invoice")
        # Delivery 2 and return 2 unit
        picking = order.picking_ids
        stock_move = order.picking_ids.move_ids
        stock_move.write({"quantity": 2, "picked": True})
        picking._action_done()
        self.assertEqual(line.qty_delivered, 2.0)
        self.assertEqual(line.qty_to_invoice, 2.0)
        WizardReturn = self.env["stock.return.picking"].with_context(
            active_model=picking._name,
            active_ids=picking.ids,
        )
        wizard = WizardReturn.create(
            {
                "picking_id": picking.id,
                "product_return_moves": [
                    Command.create(
                        {
                            "move_id": stock_move.id,
                            "product_id": stock_move.product_id.id,
                            "quantity": 2.0,
                        }
                    )
                ],
            }
        )
        new_picking = wizard._create_return()
        new_picking.move_ids.picked = True
        new_picking._action_done()
        self.assertEqual(line.qty_delivered, 0.0)
        self.assertEqual(line.qty_to_invoice, 0.0)
        self.assertEqual(line.invoice_status, "no")

    def test_fully_paid_with_returned_partial_quantity(self):
        order = self._create_sale_order(qty=2)
        line = order.order_line[0]
        self.assertEqual(line.qty_to_invoice, 0.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 0.0)
        self.assertEqual(line.amount_to_invoice, 0.0)
        self.assertEqual(line.amount_invoiced, 0.0)
        self.assertEqual(line.untaxed_amount_invoiced, 0.0)
        self.assertEqual(line.invoice_status, "no")
        self._create_done_transaction(order)
        self.assertTrue(order._is_paid())
        self.assertEqual(line.qty_to_invoice, 2.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 200.0)
        self.assertEqual(line.amount_to_invoice, 200.0)
        self.assertEqual(line.amount_invoiced, 0.0)
        self.assertEqual(line.untaxed_amount_invoiced, 0.0)
        self.assertEqual(line.invoice_status, "to invoice")
        # Delivery 2 and return 1 unit
        picking = order.picking_ids
        stock_move = order.picking_ids.move_ids
        stock_move.write({"quantity": 2, "picked": True})
        picking._action_done()
        self.assertEqual(line.qty_delivered, 2.0)
        self.assertEqual(line.qty_to_invoice, 2.0)
        WizardReturn = self.env["stock.return.picking"].with_context(
            active_model=picking._name,
            active_ids=picking.ids,
        )
        wizard = WizardReturn.create(
            {
                "picking_id": picking.id,
                "product_return_moves": [
                    Command.create(
                        {
                            "move_id": stock_move.id,
                            "product_id": stock_move.product_id.id,
                            "quantity": 1.0,
                        }
                    )
                ],
            }
        )
        new_picking = wizard._create_return()
        new_picking.move_ids.picked = True
        new_picking._action_done()
        self.assertEqual(line.qty_delivered, 1.0)
        self.assertEqual(line.qty_to_invoice, 1.0)
        invoice = order._create_invoices()
        invoice.action_post()
        invoice_line = invoice.invoice_line_ids[0]
        self.assertEqual(invoice_line.quantity, 1.0)
        self.assertEqual(line.qty_to_invoice, 0.0)
        self.assertEqual(line.qty_invoiced, 1.0)
        self.assertEqual(line.untaxed_amount_to_invoice, 0.0)
        self.assertEqual(line.amount_to_invoice, 0.0)
        self.assertEqual(line.amount_invoiced, 100.0)
        self.assertEqual(line.untaxed_amount_invoiced, 100.0)
        self.assertEqual(line.invoice_status, "invoiced")
