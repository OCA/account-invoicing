# Copyright 2026 Allied Vision Technologies Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""
Tests for account_invoice_delivery_state module.
Covers AC1–AC10 as defined in the specification.
"""

from unittest.mock import Mock

import odoo.http
from odoo import Command, fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user
from odoo.tools.misc import DotDict


@tagged("post_install", "-at_install")
class TestInvoiceDeliveryState(TransactionCase):
    """Full test suite for delivery_status / receipt_status on account.move."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # ---- Company / users ----
        cls.company = cls.env.ref("base.main_company")
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # ---- Partners ----
        cls.customer = cls.env["res.partner"].create(
            {"name": "Test Customer", "customer_rank": 1}
        )
        cls.vendor = cls.env["res.partner"].create(
            {"name": "Test Vendor", "supplier_rank": 1}
        )

        # ---- Product: storable ----
        cls.product_storable = cls.env["product.product"].create(
            {
                "name": "Storable Widget",
                "type": "consu",  # Odoo 19: storable == consu with is_storable
                "is_storable": True,
                "purchase_method": "purchase",
            }
        )

        # ---- Product: service ----
        cls.product_service = cls.env["product.product"].create(
            {"name": "Service Widget", "type": "service"}
        )

        # ---- Accounts ----
        cls.account_revenue = cls.env["account.account"].search(
            [
                ("account_type", "=", "income"),
                ("company_ids", "in", [cls.company.id]),
            ],
            limit=1,
        )
        cls.account_expense = cls.env["account.account"].search(
            [
                ("account_type", "=", "expense"),
                ("company_ids", "in", [cls.company.id]),
            ],
            limit=1,
        )

    # ------------------------------------------------------------------
    # Helper factories
    # ------------------------------------------------------------------

    def _make_sale_order(self, qty=10.0, product=None):
        """Confirm a SO and return it."""
        product = product or self.product_storable
        so = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        so.action_confirm()
        return so

    def _make_purchase_order(self, qty=10.0):
        """Confirm a PO and return it."""
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "product_qty": qty,
                            "price_unit": 80.0,
                            "date_planned": "2026-01-01",
                        }
                    )
                ],
            }
        )
        po.button_confirm()
        return po

    def _invoice_from_so(self, so):
        """Create and return a draft customer invoice from a confirmed SO."""
        so._create_invoices()
        invoice = so.invoice_ids
        self.assertEqual(len(invoice), 1)
        return invoice

    def _bill_from_po(self, po):
        """Create and return a draft vendor bill linked to a PO."""
        action = po.action_create_invoice()
        bill = self.env["account.move"].browse(action["res_id"])
        for line in bill.invoice_line_ids:
            if line.purchase_line_id and not line.quantity:
                line.quantity = line.purchase_line_id.product_qty
        return bill

    def _validate_picking_partial(self, picking, done_qty):
        """Validate a picking with done_qty < demand, creating a backorder.

        In Odoo 19, move quantity and picked status are written on stock.move,
        and backorder confirmation is processed via stock.backorder.confirmation.
        """
        for move in picking.move_ids:
            move.write({"quantity": done_qty, "picked": True})
        res = picking.button_validate()
        if (
            isinstance(res, dict)
            and res.get("res_model") == "stock.backorder.confirmation"
        ):
            wizard = (
                self.env["stock.backorder.confirmation"]
                .with_context(**res["context"])
                .create({})
            )
            wizard.process()
        return picking

    def _validate_picking_full(self, picking):
        """Validate a picking with all demand as done."""
        for move in picking.move_ids:
            move.write({"quantity": move.product_uom_qty, "picked": True})
        picking.button_validate()
        return picking

    # ------------------------------------------------------------------
    # AC1 – Customer Invoice Pending
    # ------------------------------------------------------------------

    def test_customer_invoice_delivery_pending(self):
        """T1 – delivery_status == 'pending' when no delivery is done."""
        so = self._make_sale_order(qty=10)
        invoice = self._invoice_from_so(so)
        # No picking validated yet
        self.assertEqual(invoice.delivery_status, "pending")
        self.assertTrue(invoice.has_storable_lines)

    # ------------------------------------------------------------------
    # AC2 – Customer Invoice Partial
    # ------------------------------------------------------------------

    def test_customer_invoice_delivery_partial(self):
        """T2 – delivery_status == 'partial' after backorder partial delivery."""
        so = self._make_sale_order(qty=10)
        invoice = self._invoice_from_so(so)

        picking = so.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self.assertTrue(picking, "Expected at least one delivery picking.")
        self._validate_picking_partial(picking[0], done_qty=4)

        invoice.invalidate_recordset()
        self.assertEqual(invoice.delivery_status, "partial")

    # ------------------------------------------------------------------
    # AC3 – Customer Invoice Full
    # ------------------------------------------------------------------

    def test_customer_invoice_delivery_full(self):
        """T3 – delivery_status == 'full' after complete delivery."""
        so = self._make_sale_order(qty=10)
        invoice = self._invoice_from_so(so)

        picking = so.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self._validate_picking_full(picking[0])

        invoice.invalidate_recordset()
        self.assertEqual(invoice.delivery_status, "full")

    # ------------------------------------------------------------------
    # AC4 – Service Products Exclusion
    # ------------------------------------------------------------------

    def test_service_invoice_no_delivery_status(self):
        """T4 – delivery_status is False for service-only invoice."""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_service.id,
                            "name": "Service",
                            "quantity": 1.0,
                            "price_unit": 50.0,
                            "account_id": self.account_revenue.id,
                        }
                    )
                ],
            }
        )
        self.assertFalse(invoice.delivery_status)
        self.assertFalse(invoice.has_storable_lines)

    # ------------------------------------------------------------------
    # AC5 – Vendor Bill Pending
    # ------------------------------------------------------------------

    def test_vendor_bill_receipt_pending(self):
        """T5 – receipt_status == 'pending' when no receipt is done."""
        po = self._make_purchase_order(qty=10)
        bill = self._bill_from_po(po)
        self.assertEqual(bill.receipt_status, "pending")

    # ------------------------------------------------------------------
    # AC6 – Vendor Bill Partial
    # ------------------------------------------------------------------

    def test_vendor_bill_receipt_partial(self):
        """T6 – receipt_status == 'partial' after a partial incoming receipt."""
        po = self._make_purchase_order(qty=10)
        bill = self._bill_from_po(po)

        picking = po.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self.assertTrue(picking, "Expected incoming receipt picking.")
        self._validate_picking_partial(picking[0], done_qty=3)

        bill.invalidate_recordset()
        self.assertEqual(bill.receipt_status, "partial")

    # ------------------------------------------------------------------
    # AC7 – Vendor Bill Full
    # ------------------------------------------------------------------

    def test_vendor_bill_receipt_full(self):
        """T7 – receipt_status == 'full' after full incoming receipt."""
        po = self._make_purchase_order(qty=10)
        bill = self._bill_from_po(po)

        picking = po.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self._validate_picking_full(picking[0])

        bill.invalidate_recordset()
        self.assertEqual(bill.receipt_status, "full")

    # ------------------------------------------------------------------
    # AC8 – Standalone Invoices / Bills
    # ------------------------------------------------------------------

    def test_standalone_invoice_and_bill(self):
        """T8 – delivery_status and receipt_status are False for standalone docs."""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "name": "Widget",
                            "quantity": 5.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                        }
                    )
                ],
            }
        )
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "name": "Widget",
                            "quantity": 5.0,
                            "price_unit": 80.0,
                            "account_id": self.account_expense.id,
                        }
                    )
                ],
            }
        )
        # No SO / PO linked → should be False
        self.assertFalse(invoice.delivery_status)
        self.assertFalse(bill.receipt_status)

    # ------------------------------------------------------------------
    # AC9 – Search & Filter
    # ------------------------------------------------------------------

    def test_search_filters_and_grouping(self):
        """T9 – Domain search and read_group on delivery_status and receipt_status."""
        so = self._make_sale_order(qty=10)
        invoice = self._invoice_from_so(so)
        # Invoice should be pending
        self.assertEqual(invoice.delivery_status, "pending")

        # Domain search returns the record
        pending_invoices = self.env["account.move"].search(
            [
                ("id", "=", invoice.id),
                ("delivery_status", "=", "pending"),
            ]
        )
        self.assertIn(invoice, pending_invoices)

        # Verify Group By delivery_status via read_group
        grouped_invoices = self.env["account.move"].read_group(
            domain=[("id", "=", invoice.id)],
            fields=["delivery_status"],
            groupby=["delivery_status"],
        )
        self.assertTrue(
            any(g["delivery_status"] == "pending" for g in grouped_invoices)
        )

        po = self._make_purchase_order(qty=10)
        bill = self._bill_from_po(po)
        picking = po.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self._validate_picking_full(picking[0])
        bill.invalidate_recordset()

        self.assertEqual(bill.receipt_status, "full")
        full_bills = self.env["account.move"].search(
            [
                ("id", "=", bill.id),
                ("receipt_status", "=", "full"),
            ]
        )
        self.assertIn(bill, full_bills)

        # Verify Group By receipt_status via read_group
        grouped_bills = self.env["account.move"].read_group(
            domain=[("id", "=", bill.id)],
            fields=["receipt_status"],
            groupby=["receipt_status"],
        )
        self.assertTrue(any(g["receipt_status"] == "full" for g in grouped_bills))

    # ------------------------------------------------------------------
    # AC10 – Portal display & privacy
    # ------------------------------------------------------------------

    def test_portal_delivery_status_display(self):
        """T10 – Portal user sees delivery_status badge on /my/invoices and detail
        page without technical stock move/picking details exposed; service-only
        invoice does not show delivery status badge."""
        so = self._make_sale_order(qty=5)
        invoice = self._invoice_from_so(so)
        invoice.action_post()

        # Create authenticated portal customer using supported Odoo 19 API
        portal_user = new_test_user(
            self.env,
            login="portal_customer_ac10_test",
            groups="base.group_portal",
            partner_id=self.customer.id,
        )

        # 1. Field value validity
        self.assertEqual(invoice.delivery_status, "pending")
        self.assertIsInstance(invoice.delivery_status, str)

        # Service-only invoice created beforehand
        svc_invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_service.id,
                            "name": "Consulting",
                            "quantity": 1.0,
                            "price_unit": 200.0,
                            "account_id": self.account_revenue.id,
                        }
                    )
                ],
            }
        )
        svc_invoice.action_post()
        self.assertFalse(svc_invoice.delivery_status)

        # Setup mock HTTP request context for portal QWeb rendering in TransactionCase
        mock_req = Mock(
            type="http",
            params={},
            uid=portal_user.id,
            session=DotDict(
                odoo.http.get_default_session(),
                debug="",
                uid=portal_user.id,
                context={"lang": "en_US"},
            ),
            env=self.env,
            lang=self.env["res.lang"]._get_data(code="en_US"),
        )
        odoo.http._request_stack.push(mock_req)
        try:
            # 2. Render portal list template (account.portal_my_invoices)
            html_list = (
                self.env["ir.qweb"]
                .with_user(portal_user)
                ._render(
                    "account.portal_my_invoices",
                    {"invoices": [{"invoice": invoice}]},
                )
            )
            self.assertIn("Delivery", html_list)
            self.assertIn("Not Delivered", html_list)

            # Verify zero stock picking or move technical IDs leaked to portal user
            for picking in so.picking_ids:
                self.assertNotIn(picking.name, html_list)

            # 3. Render portal invoice page sidebar (account.portal_invoice_page)
            html_detail = (
                self.env["ir.qweb"]
                .with_user(portal_user)
                ._render(
                    "account.portal_invoice_page",
                    {
                        "invoice": invoice,
                        "object": invoice,
                        "payment_state": invoice.payment_state,
                        "is_last_installment": True,
                        "installment_state": False,
                        "amount_due": invoice.amount_residual,
                        "due_date": invoice.invoice_date_due,
                        "currency": invoice.currency_id,
                        "tokens_sudo": self.env["payment.token"],
                        "payment_methods_sudo": self.env["payment.method"],
                    },
                )
            )
            self.assertIn("Delivery Status", html_detail)
            self.assertIn("Not Delivered", html_detail)
            for picking in so.picking_ids:
                self.assertNotIn(picking.name, html_detail)

            # 4. Service-only invoice must not expose delivery_status badge
            svc_html_list = (
                self.env["ir.qweb"]
                .with_user(portal_user)
                ._render(
                    "account.portal_my_invoices",
                    {"invoices": [{"invoice": svc_invoice}]},
                )
            )
            self.assertNotIn("Not Delivered", svc_html_list)
            self.assertNotIn("Fully Delivered", svc_html_list)
            self.assertNotIn("Partially Delivered", svc_html_list)
        finally:
            odoo.http._request_stack.pop()

    # ------------------------------------------------------------------
    # Additional Verification: Refunds, Storability Change & NewId Safety
    # ------------------------------------------------------------------

    def test_credit_note_refund_no_delivery_or_receipt_status(self):
        """Customer credit notes (out_refund) and vendor refunds (in_refund)
        must have delivery_status = False and receipt_status = False."""
        cust_refund = self.env["account.move"].create(
            {
                "move_type": "out_refund",
                "partner_id": self.customer.id,
                "invoice_date": fields.Date.context_today(self.env.user),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "name": "Refund Line",
                            "quantity": 2.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                        }
                    )
                ],
            }
        )
        cust_refund.action_post()
        self.assertFalse(cust_refund.delivery_status)

        vendor_refund = self.env["account.move"].create(
            {
                "move_type": "in_refund",
                "partner_id": self.vendor.id,
                "invoice_date": fields.Date.context_today(self.env.user),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "name": "Vendor Refund Line",
                            "quantity": 2.0,
                            "price_unit": 80.0,
                            "account_id": self.account_expense.id,
                        }
                    )
                ],
            }
        )
        vendor_refund.action_post()
        self.assertFalse(vendor_refund.receipt_status)

    def test_product_storability_change_triggers_recomputation(self):
        """Toggling is_storable on a product dynamically triggers has_storable_lines
        and delivery_status recomputations without changing product type."""
        prod = self.env["product.product"].create(
            {
                "name": "Toggle Consu Widget",
                "type": "consu",
                "is_storable": False,
            }
        )
        so = self._make_sale_order(qty=5.0, product=prod)
        inv = self._invoice_from_so(so)
        self.assertFalse(inv.has_storable_lines)
        self.assertFalse(inv.delivery_status)

        # Switch product to storable while keeping type = 'consu'
        prod.is_storable = True
        inv.invalidate_recordset()
        self.assertTrue(inv.has_storable_lines)
        self.assertEqual(inv.delivery_status, "pending")

    def test_in_memory_newid_fifo_sorting(self):
        """Verify FIFO allocation methods handle unsaved/in-memory records with NewId
        without raising TypeError."""
        so = self._make_sale_order(qty=10.0)
        sol = so.order_line[0]

        # First invoice persisted in DB
        self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 5.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "sale_line_ids": [Command.link(sol.id)],
                        }
                    )
                ],
            }
        )

        # Second invoice in memory (NewId) with identical date
        inv2_line = self.env["account.move.line"].new(
            {
                "display_type": "product",
                "product_id": self.product_storable.id,
                "quantity": 5.0,
                "product_uom_id": self.product_storable.uom_id.id,
                "sale_line_ids": [Command.link(sol.id)],
            }
        )
        inv2 = self.env["account.move"].new(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [inv2_line],
            }
        )
        inv2_line.move_id = inv2

        # Executing FIFO allocation on lines containing NewId must not raise TypeError
        alloc = inv2._allocate_delivered_quantities_fifo(inv2_line)
        self.assertIsInstance(alloc, dict)

    # ------------------------------------------------------------------
    # Multi-invoice Chronological Allocation & Regression Tests
    # ------------------------------------------------------------------

    def test_multiple_invoices_chronological_delivery_allocation(self):
        """Test chronological FIFO delivery allocation across sibling invoices.

        Scenario:
        - SO: 8 units ordered, 5 units delivered.
        - Inv1 (4 units, earlier date) -> 'full' (4/4 delivered).
        - Inv2 (4 units, later date) -> 'partial' (1/4 delivered).
        - Deliver remaining 3 units -> Inv2 recomputes to 'full'.
        """
        so = self._make_sale_order(qty=8.0)
        sol = so.order_line[0]

        # Deliver 5 of 8 units
        picking = so.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self._validate_picking_partial(picking[0], done_qty=5.0)

        # Invoice 1 on Day 1 (4 units)
        inv1 = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": "2026-11-01",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 4.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "sale_line_ids": [Command.link(sol.id)],
                        }
                    )
                ],
            }
        )

        # Invoice 2 on Day 2 (4 units)
        inv2 = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": "2026-11-02",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 4.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "sale_line_ids": [Command.link(sol.id)],
                        }
                    )
                ],
            }
        )

        self.assertEqual(inv1.delivery_status, "full")
        self.assertEqual(inv2.delivery_status, "partial")

        # Deliver remaining 3 units (backorder)
        backorder = so.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self.assertTrue(backorder)
        self._validate_picking_full(backorder[0])

        inv1.invalidate_recordset()
        inv2.invalidate_recordset()
        self.assertEqual(inv1.delivery_status, "full")
        self.assertEqual(inv2.delivery_status, "full")

    def test_multiple_bills_chronological_receipt_allocation(self):
        """Test chronological FIFO receipt allocation across sibling vendor bills.

        Scenario:
        - PO: 8 units ordered, 5 units received.
        - Bill 1 (4 units, earlier date) -> 'full'.
        - Bill 2 (4 units, later date) -> 'partial' (1/4 received).
        - Receive remaining 3 units -> Bill 2 recomputes to 'full'.
        """
        po = self._make_purchase_order(qty=8.0)
        pol = po.order_line[0]

        # Receive 5 of 8 units
        picking = po.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self._validate_picking_partial(picking[0], done_qty=5.0)

        bill1 = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "invoice_date": "2026-11-01",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 4.0,
                            "price_unit": 80.0,
                            "account_id": self.account_expense.id,
                            "purchase_line_id": pol.id,
                        }
                    )
                ],
            }
        )

        bill2 = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "invoice_date": "2026-11-02",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 4.0,
                            "price_unit": 80.0,
                            "account_id": self.account_expense.id,
                            "purchase_line_id": pol.id,
                        }
                    )
                ],
            }
        )

        self.assertEqual(bill1.receipt_status, "full")
        self.assertEqual(bill2.receipt_status, "partial")

        # Receive remaining 3 units
        backorder = po.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self._validate_picking_full(backorder[0])

        bill1.invalidate_recordset()
        bill2.invalidate_recordset()
        self.assertEqual(bill1.receipt_status, "full")
        self.assertEqual(bill2.receipt_status, "full")

    def test_draft_invoices_reserve_delivery_capacity_and_cancel_recomputes(self):
        """Test that draft invoices reserve delivery capacity, and cancelling
        an earlier invoice releases its allocation to subsequent invoices.
        """
        so = self._make_sale_order(qty=8.0)
        sol = so.order_line[0]

        picking = so.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self._validate_picking_partial(picking[0], done_qty=5.0)

        inv1 = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": "2026-11-01",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 4.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "sale_line_ids": [Command.link(sol.id)],
                        }
                    )
                ],
            }
        )

        inv2 = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": "2026-11-02",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 4.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "sale_line_ids": [Command.link(sol.id)],
                        }
                    )
                ],
            }
        )

        # Both are draft, but inv1 takes precedence by date/ID
        self.assertEqual(inv1.state, "draft")
        self.assertEqual(inv2.state, "draft")
        self.assertEqual(inv1.delivery_status, "full")
        self.assertEqual(inv2.delivery_status, "partial")

        # Cancel inv1: its reserved delivery should be released
        inv1.button_cancel()
        inv1.invalidate_recordset()
        inv2.invalidate_recordset()

        self.assertFalse(inv1.delivery_status)
        # inv2 now receives 4 of the 5 available units -> full
        self.assertEqual(inv2.delivery_status, "full")

    def test_invoice_date_reordering_recomputes_delivery_status(self):
        """Test that changing invoice dates dynamically reorders FIFO allocation."""
        so = self._make_sale_order(qty=8.0)
        sol = so.order_line[0]

        picking = so.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        self._validate_picking_partial(picking[0], done_qty=5.0)

        inv1 = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": "2026-11-05",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 4.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "sale_line_ids": [Command.link(sol.id)],
                        }
                    )
                ],
            }
        )

        inv2 = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": "2026-11-06",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 4.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "sale_line_ids": [Command.link(sol.id)],
                        }
                    )
                ],
            }
        )

        self.assertEqual(inv1.delivery_status, "full")
        self.assertEqual(inv2.delivery_status, "partial")

        # Move inv2 to an earlier date than inv1
        inv2.write({"invoice_date": "2026-11-01"})
        inv1.invalidate_recordset()
        inv2.invalidate_recordset()

        # inv2 should now be full (first in FIFO) and inv1 partial
        self.assertEqual(inv2.delivery_status, "full")
        self.assertEqual(inv1.delivery_status, "partial")

    def test_multi_sales_order_lines_m2m_no_over_allocation(self):
        """Test that an invoice line linked to multiple sales order lines
        accumulates delivered quantity without over-consuming.
        """
        so = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "product_uom_qty": 4.0,
                            "price_unit": 100.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "product_uom_qty": 4.0,
                            "price_unit": 100.0,
                        }
                    ),
                ],
            }
        )
        so.action_confirm()
        sol1, sol2 = so.order_line[0], so.order_line[1]

        # Deliver 3 on sol1 and 2 on sol2 -> total 5 delivered
        picking = so.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        moves = picking[0].move_ids
        moves[0].write({"quantity": 3.0, "picked": True})
        moves[1].write({"quantity": 2.0, "picked": True})
        res = picking[0].button_validate()
        if (
            isinstance(res, dict)
            and res.get("res_model") == "stock.backorder.confirmation"
        ):
            self.env["stock.backorder.confirmation"].with_context(
                **res["context"]
            ).create({}).process()

        # Single invoice line grouping both SOLs (total 8 units)
        inv = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": "2026-11-01",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 8.0,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "sale_line_ids": [
                                Command.link(sol1.id),
                                Command.link(sol2.id),
                            ],
                        }
                    )
                ],
            }
        )

        # 5 out of 8 delivered -> partial
        self.assertEqual(inv.delivery_status, "partial")

    def test_multi_uom_delivery_conversion(self):
        """Test UoM conversions across sales order and invoice lines."""
        uom_dozen = self.env.ref("uom.product_uom_dozen")
        uom_unit = self.env.ref("uom.product_uom_unit")

        prod_uom = self.env["product.product"].create(
            {
                "name": "Widget UoM",
                "type": "consu",
                "is_storable": True,
                "uom_id": uom_unit.id,
            }
        )

        # SO in Dozens (1 Dozen = 12 Units)
        so = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": prod_uom.id,
                            "product_uom_qty": 1.0,
                            "product_uom_id": uom_dozen.id,
                            "price_unit": 120.0,
                        }
                    )
                ],
            }
        )
        so.action_confirm()
        sol = so.order_line[0]

        # Deliver 6 Units (= 0.5 Dozen). Stock moves are tracked in base UoM (Units).
        picking = so.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
        picking[0].move_ids.write({"quantity": 6.0, "picked": True})
        res = picking[0].button_validate()
        if (
            isinstance(res, dict)
            and res.get("res_model") == "stock.backorder.confirmation"
        ):
            self.env["stock.backorder.confirmation"].with_context(
                **res["context"]
            ).create({}).process()

        # Invoice in Units (6 Units)
        inv = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_date": "2026-11-01",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": prod_uom.id,
                            "quantity": 6.0,
                            "product_uom_id": uom_unit.id,
                            "price_unit": 10.0,
                            "account_id": self.account_revenue.id,
                            "sale_line_ids": [Command.link(sol.id)],
                        }
                    )
                ],
            }
        )

        # 6 units invoiced, 6 units delivered -> full
        self.assertEqual(inv.delivery_status, "full")
