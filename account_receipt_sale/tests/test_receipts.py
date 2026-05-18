# Copyright 2018 Simone Rubino
# Copyright 2022 Lorenzo Battistini
# Copyright 2023 Simone Rubino - TAKOBI
# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account_receipt_journal.tests.test_receipts import TestReceipts


@tagged("post_install", "-at_install")
class TestReceiptsSale(TestReceipts):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.receipt_partner = cls.env["res.partner"].create(
            {"name": "Receipt partner", "use_receipts": True}
        )
        cls.no_receipt_partner = cls.env["res.partner"].create(
            {"name": "No receipt partner", "use_receipts": False}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "list_price": 100.0, "taxes_id": False}
        )

    def _create_order(self, partner):
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

    def _open_wizard(self, orders, **values):
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=orders.ids, active_model="sale.order")
            .create(values)
        )
        return wizard

    def test_order_partner_default(self):
        order_receipts = self._create_order(self.receipt_partner)
        self.assertTrue(order_receipts.receipts)
        order_no_receipts = self._create_order(self.no_receipt_partner)
        self.assertFalse(order_no_receipts.receipts)
        order_no_receipts.partner_id = self.receipt_partner
        self.assertTrue(order_no_receipts.receipts)
        order_no_receipts.partner_id = self.no_receipt_partner
        self.assertFalse(order_no_receipts.receipts)

    def test_order_fiscal_position_default(self):
        receipt_fp = self.env["account.fiscal.position"].create(
            {"name": "Receipts FP", "receipts": True}
        )
        no_receipt_fp = self.env["account.fiscal.position"].create(
            {"name": "No Receipts FP", "receipts": False}
        )
        order = self._create_order(self.no_receipt_partner)
        self.assertFalse(order.receipts)
        order.fiscal_position_id = receipt_fp
        self.assertTrue(order.receipts)
        order.fiscal_position_id = no_receipt_fp
        self.assertFalse(order.receipts)

    def test_create_receipt_delivered(self):
        order = self._create_order(self.receipt_partner)
        order.action_confirm()
        order.order_line.qty_delivered = 1.0
        wizard = self._open_wizard(order, advance_payment_method="delivered")
        wizard.create_invoices()
        receipt = order.receipt_ids
        self.assertEqual(len(receipt), 1)
        self.assertEqual(receipt.move_type, "out_receipt")
        self.assertTrue(receipt.journal_id.receipts)

    def test_create_receipt_down_payment(self):
        # The 'percentage' / 'fixed' down-payment paths build the invoice
        # values inside the wizard via _prepare_invoice_values and never
        # call sale.order._prepare_invoice, so the override that flips
        # move_type to out_receipt must live on the wizard too. This test
        # guards that wizard-side override; the 'delivered' tests above
        # only exercise the sale.order side.
        order = self._create_order(self.receipt_partner)
        order.action_confirm()
        wizard = self._open_wizard(
            order,
            advance_payment_method="percentage",
            amount=50.0,
        )
        wizard.create_invoices()
        self.assertEqual(len(order.receipt_ids), 1)
        self.assertEqual(order.receipt_ids.move_type, "out_receipt")

    def test_create_invoice_down_payment(self):
        # Counterpart of test_create_receipt_down_payment: when receipts is
        # False, the down-payment path must still produce a regular invoice.
        order = self._create_order(self.no_receipt_partner)
        order.action_confirm()
        wizard = self._open_wizard(
            order,
            advance_payment_method="percentage",
            amount=50.0,
        )
        wizard.create_invoices()
        self.assertEqual(len(order.invoice_ids), 1)
        self.assertEqual(order.invoice_ids.move_type, "out_invoice")
        self.assertFalse(order.receipt_ids)

    def test_order_creation_with_fiscal_position(self):
        # Exercises the create() override branch that fires the
        # fiscal_position_id onchange when the FP is provided at creation
        # time (the other tests only mutate it post-create via write).
        receipt_fp = self.env["account.fiscal.position"].create(
            {"name": "Receipts FP at create", "receipts": True}
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.no_receipt_partner.id,
                "fiscal_position_id": receipt_fp.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        self.assertTrue(order.receipts)

    def test_search_receipt_ids(self):
        # Exercises the three branches of _search_receipt_ids: 'in' SQL
        # branch, '= False' (orders without receipts), and the default
        # branch ('!=' False, etc.).
        order = self._create_order(self.receipt_partner)
        order.action_confirm()
        order.order_line.qty_delivered = 1.0
        self._open_wizard(order, advance_payment_method="delivered").create_invoices()
        receipt = order.receipt_ids
        order_no_receipts = self._create_order(self.no_receipt_partner)
        # 'in' branch
        found_in = self.env["sale.order"].search([("receipt_ids", "in", receipt.ids)])
        self.assertIn(order, found_in)
        # '= False' branch
        found_empty = self.env["sale.order"].search([("receipt_ids", "=", False)])
        self.assertIn(order_no_receipts, found_empty)
        self.assertNotIn(order, found_empty)
        # default branch
        found_any = self.env["sale.order"].search([("receipt_ids", "!=", False)])
        self.assertIn(order, found_any)

    def test_action_view_receipt_branches(self):
        # Covers the len(receipts) == 0 and len(receipts) > 1 branches
        # of action_view_receipt; the len == 1 branch is exercised by
        # test_create_receipt_delivered via the wizard return path.
        empty_order = self._create_order(self.receipt_partner)
        action = empty_order.action_view_receipt()
        self.assertEqual(action["type"], "ir.actions.act_window_close")

        order_a = self._create_order(self.receipt_partner)
        order_b = self._create_order(self.receipt_partner)
        for order in (order_a, order_b):
            order.action_confirm()
            order.order_line.qty_delivered = 1.0
            self._open_wizard(
                order, advance_payment_method="delivered"
            ).create_invoices()
        receipts = (order_a + order_b).receipt_ids
        self.assertEqual(len(receipts), 2)
        action = (order_a + order_b).action_view_receipt()
        self.assertEqual(action["domain"], [("id", "in", receipts.ids)])

    def test_qty_and_amount_invoiced_rollup(self):
        # test `_compute_qty_invoiced` and `_compute_untaxed_amount_invoiced` override:
        # ensure that qty_invoiced and untaxed_amount_invoiced are computed when
        # invoice lines move_type is `out_receipt`
        order = self._create_order(self.receipt_partner)
        order.action_confirm()
        order.order_line.qty_delivered = 1.0
        wizard = self._open_wizard(order, advance_payment_method="delivered")
        wizard.create_invoices()
        receipt = order.receipt_ids
        receipt.action_post()
        self.assertEqual(order.order_line.qty_invoiced, 1.0)
        self.assertEqual(order.order_line.untaxed_amount_invoiced, 100.0)
