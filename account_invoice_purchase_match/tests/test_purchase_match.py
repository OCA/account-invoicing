# Copyright 2026 OSS Factory
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseMatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Move = cls.env["account.move"]
        cls.Match = cls.env["purchase.bill.line.match"]
        cls.vendor = cls.env["res.partner"].create(
            {"name": "Vendor Match Test", "is_company": True}
        )
        cls.product_a = cls.env["product.product"].create(
            {"name": "Product A", "type": "consu", "purchase_method": "purchase"}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "Product B", "type": "consu", "purchase_method": "purchase"}
        )
        cls.product_c = cls.env["product.product"].create(
            {"name": "Product C", "type": "consu", "purchase_method": "purchase"}
        )

        # Confirmed purchase order with two product lines (A and B).
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_a.id,
                            "product_qty": 5,
                            "price_unit": 10.0,
                            "name": "PO A",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_b.id,
                            "product_qty": 3,
                            "price_unit": 20.0,
                            "name": "PO B",
                        },
                    ),
                ],
            },
        )
        cls.po.button_confirm()
        cls.po_line_a = cls.po.order_line.filtered(
            lambda line: line.product_id == cls.product_a
        )
        cls.po_line_b = cls.po.order_line.filtered(
            lambda line: line.product_id == cls.product_b
        )

    def _draft_bill(self, products):
        return self.Move.create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": p.id,
                            "name": p.name,
                            "quantity": 1,
                            "price_unit": 10.0,
                        },
                    )
                    for p in products
                ],
            },
        )

    def _match_rows(self, move):
        """Mimic action_purchase_matching: the rows the user would see."""
        partner = move.partner_id | move.partner_id.commercial_partner_id
        return self.Match.search(
            [
                ("partner_id", "in", partner.ids),
                ("account_move_id", "in", [move.id, False]),
            ],
        )

    def _pol_rows(self, rows, po_line):
        return rows.filtered(lambda r: r.pol_id == po_line)

    def _aml_rows(self, rows, move_line):
        return rows.filtered(lambda r: r.aml_id == move_line)

    # ------------------------------------------------------------------
    # SQL view
    # ------------------------------------------------------------------
    def test_view_unions_po_and_bill_lines(self):
        """The view exposes both the open PO lines and the unlinked bill lines."""
        bill = self._draft_bill([self.product_a])
        rows = self._match_rows(bill)
        pol_rows = rows.filtered(lambda r: r.pol_id)
        aml_rows = rows.filtered(lambda r: r.aml_id)
        self.assertIn(self.po_line_a, pol_rows.mapped("pol_id"))
        self.assertIn(self.po_line_b, pol_rows.mapped("pol_id"))
        bill_line_a = bill.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product_a
        )
        self.assertIn(bill_line_a, aml_rows.mapped("aml_id"))
        # PO rows carry the purchase side, AML rows the bill side.
        po_row_a = self._pol_rows(rows, self.po_line_a)
        self.assertEqual(po_row_a.purchase_order_id, self.po)
        self.assertFalse(po_row_a.account_move_id)
        self.assertTrue(po_row_a.purchase_amount_untaxed)
        self.assertFalse(po_row_a.billed_amount_untaxed)

    # ------------------------------------------------------------------
    # action_match_lines
    # ------------------------------------------------------------------
    def test_match_links_bill_line_to_po_line(self):
        """Selecting a PO line + a same-product bill line links them."""
        bill = self._draft_bill([self.product_a])
        bill_line_a = bill.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product_a
        )
        rows = self._match_rows(bill)
        selection = self._pol_rows(rows, self.po_line_a) | self._aml_rows(
            rows, bill_line_a
        )
        selection.action_match_lines()
        self.assertEqual(bill_line_a.purchase_line_id, self.po_line_a)

    def test_match_picks_earliest_po_line_for_duplicate_product(self):
        """With several PO lines of the same product, only the first matches."""
        po2 = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "product_qty": 2,
                            "price_unit": 11.0,
                            "name": "PO2 A",
                        },
                    )
                ],
            },
        )
        po2.button_confirm()
        po2_line_a = po2.order_line
        bill = self._draft_bill([self.product_a])
        bill_line_a = bill.invoice_line_ids
        rows = self._match_rows(bill)
        selection = (
            self._pol_rows(rows, self.po_line_a)
            | self._pol_rows(rows, po2_line_a)
            | self._aml_rows(rows, bill_line_a)
        )
        selection.action_match_lines()
        self.assertIn(bill_line_a.purchase_line_id, self.po_line_a | po2_line_a)
        # Exactly one of them is linked, not both.
        self.assertEqual(len(bill_line_a.purchase_line_id), 1)

    def test_match_adds_residual_po_line_to_bill(self):
        """A selected PO line with no bill counterpart is added to the bill."""
        bill = self._draft_bill([self.product_a])
        bill_line_a = bill.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product_a
        )
        # Captured BEFORE matching: once the residual line is created and linked,
        # po_line_b.qty_to_invoice recomputes (the new draft line counts in
        # qty_invoiced), so reading it after the match would be a moving target.
        expected_qty = self.po_line_b.qty_to_invoice
        rows = self._match_rows(bill)
        selection = (
            self._pol_rows(rows, self.po_line_a)
            | self._pol_rows(rows, self.po_line_b)
            | self._aml_rows(rows, bill_line_a)
        )
        selection.action_match_lines()
        new_line = bill.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product_b
        )
        self.assertTrue(
            new_line, "Product B PO line should have been added to the bill"
        )
        self.assertEqual(new_line.purchase_line_id, self.po_line_b)
        # qty pulled from the PO line's qty_to_invoice (faithful to Odoo 19.0)
        self.assertEqual(new_line.quantity, expected_qty)

    def test_match_removes_unmatched_selected_bill_line(self):
        """An unmatched selected bill line is removed when a single bill is involved."""
        bill = self._draft_bill([self.product_c])  # product C is not on any PO
        bill_line_c = bill.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product_c
        )
        rows = self._match_rows(bill)
        # Select PO line A (residual, will be added) + the orphan bill line C.
        selection = self._pol_rows(rows, self.po_line_a) | self._aml_rows(
            rows, bill_line_c
        )
        selection.action_match_lines()
        self.assertFalse(
            bill_line_c.exists(), "Unmatched selected bill line C must be removed"
        )
        added = bill.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product_a
        )
        self.assertEqual(added.purchase_line_id, self.po_line_a)

    def test_match_po_lines_only_creates_new_bill(self):
        """Selecting only PO lines (no bill line) creates a new draft bill."""
        rows = self.Match.search(
            [("partner_id", "=", self.vendor.id), ("pol_id", "!=", False)]
        )
        selection = self._pol_rows(rows, self.po_line_a) | self._pol_rows(
            rows, self.po_line_b
        )
        action = selection.action_match_lines()
        self.assertEqual(action["res_model"], "account.move")
        new_bill = self.Move.browse(action["res_id"])
        self.assertEqual(new_bill.move_type, "in_invoice")
        self.assertEqual(new_bill.partner_id, self.vendor)
        linked = new_bill.invoice_line_ids.mapped("purchase_line_id")
        self.assertEqual(linked, self.po_line_a | self.po_line_b)

    def test_match_without_po_line_raises(self):
        """Matching with only bill lines selected is not allowed."""
        bill = self._draft_bill([self.product_a])
        rows = self._match_rows(bill)
        selection = self._aml_rows(rows, bill.invoice_line_ids)
        with self.assertRaises(UserError):
            selection.action_match_lines()

    # ------------------------------------------------------------------
    # inverse editable columns
    # ------------------------------------------------------------------
    def test_inverse_qty_and_price_write_back(self):
        """Editing qty/price on the view writes back to the bill line."""
        bill = self._draft_bill([self.product_a])
        bill_line_a = bill.invoice_line_ids
        row = self._aml_rows(self._match_rows(bill), bill_line_a)
        row.product_uom_qty = 7
        row._inverse_product_uom_qty()
        row.product_uom_price = 12.5
        row._inverse_product_uom_price()
        self.assertEqual(bill_line_a.quantity, 7)
        self.assertEqual(bill_line_a.price_unit, 12.5)

    # ------------------------------------------------------------------
    # bill smart button visibility
    # ------------------------------------------------------------------
    def test_is_purchase_matched_flag(self):
        """The flag is False while a product line is unlinked, True once all are linked."""
        bill = self._draft_bill([self.product_a])
        self.assertFalse(bill.is_purchase_matched)
        bill_line_a = bill.invoice_line_ids
        rows = self._match_rows(bill)
        (
            self._pol_rows(rows, self.po_line_a) | self._aml_rows(rows, bill_line_a)
        ).action_match_lines()
        self.assertTrue(bill.is_purchase_matched)

    def test_action_purchase_matching_returns_view(self):
        """The smart button returns an action on the matching model."""
        bill = self._draft_bill([self.product_a])
        action = bill.action_purchase_matching()
        self.assertEqual(action["res_model"], "purchase.bill.line.match")
        self.assertTrue(
            any(
                d[0] == "partner_id"
                for d in action["domain"]
                if isinstance(d, (list, tuple))
            )
        )

    def test_open_line_action(self):
        """action_open_line jumps to the PO (or bill) of the row."""
        bill = self._draft_bill([self.product_a])
        po_row = self._pol_rows(self._match_rows(bill), self.po_line_a)
        action = po_row.action_open_line()
        self.assertEqual(action["res_model"], "purchase.order")
        self.assertEqual(action["res_id"], self.po.id)
        aml_row = self._aml_rows(self._match_rows(bill), bill.invoice_line_ids)
        action2 = aml_row.action_open_line()
        self.assertEqual(action2["res_model"], "account.move")
        self.assertEqual(action2["res_id"], bill.id)

    # ------------------------------------------------------------------
    # Add to PO (bill.to.po.wizard.action_add_to_po)
    # ------------------------------------------------------------------
    def _run_add_to_po(self, match_rows, purchase_order=None):
        """Mimic the matching screen "Add to PO" button.

        ``action_add_to_po`` on the match model builds the wizard action and
        passes the selected match record ids as ``active_ids`` (account move
        rows carry a negative id, ``id = -aml.id``). We replay that here: build
        the wizard with the same context and run its ``action_add_to_po``.
        """
        match_action = match_rows.action_add_to_po()
        ctx = match_action["context"]
        wizard_vals = {}
        if purchase_order is not None:
            wizard_vals["purchase_order_id"] = purchase_order.id
        elif ctx.get("default_purchase_order_id"):
            wizard_vals["purchase_order_id"] = ctx["default_purchase_order_id"]
        if ctx.get("default_partner_id"):
            wizard_vals["partner_id"] = ctx["default_partner_id"]
        wizard = (
            self.env["bill.to.po.wizard"]
            .with_context(active_ids=ctx["active_ids"])
            .create(wizard_vals)
        )
        return wizard.action_add_to_po()

    def test_add_to_po_new_order(self):
        """Add to PO with no target order creates and confirms a new PO."""
        bill = self._draft_bill([self.product_a])
        bill_line_a = bill.invoice_line_ids
        bill_line_a.write({"quantity": 4, "price_unit": 12.5})
        aml_row = self._aml_rows(self._match_rows(bill), bill_line_a)
        action = self._run_add_to_po(aml_row)
        self.assertEqual(action["res_model"], "purchase.order")
        new_po = self.env["purchase.order"].browse(action["res_id"])
        self.assertEqual(new_po.partner_id, self.vendor)
        self.assertEqual(new_po.state, "purchase", "New PO must be confirmed")
        new_pol = new_po.order_line.filtered(
            lambda line: line.product_id == self.product_a
        )
        self.assertEqual(len(new_pol), 1)
        self.assertEqual(new_pol.product_qty, 4)
        self.assertEqual(new_pol.price_unit, 12.5)
        self.assertEqual(
            bill_line_a.purchase_line_id,
            new_pol,
            "Bill line must be linked to the new PO line",
        )

    def test_add_to_po_existing_order(self):
        """Add to PO targeting an existing order appends the lines to it."""
        bill = self._draft_bill([self.product_c])  # product C is not yet on self.po
        bill_line_c = bill.invoice_line_ids
        aml_row = self._aml_rows(self._match_rows(bill), bill_line_c)
        lines_before = self.po.order_line
        action = self._run_add_to_po(aml_row, purchase_order=self.po)
        self.assertEqual(action["res_id"], self.po.id)
        new_pol = self.po.order_line - lines_before
        self.assertEqual(len(new_pol), 1)
        self.assertEqual(new_pol.product_id, self.product_c)
        self.assertEqual(bill_line_c.purchase_line_id, new_pol)

    def test_add_to_po_preserves_amounts_taxes_uom(self):
        """Product, qty, price, taxes and UoM are carried onto the PO line."""
        tax = self.env["account.tax"].create(
            {
                "name": "Test Purchase Tax 10",
                "amount": 10.0,
                "type_tax_use": "purchase",
            },
        )
        bill = self.Move.create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "name": self.product_a.name,
                            "quantity": 2,
                            "price_unit": 15.0,
                            "tax_ids": [(6, 0, tax.ids)],
                        },
                    ),
                ],
            },
        )
        bill_line_a = bill.invoice_line_ids
        aml_row = self._aml_rows(self._match_rows(bill), bill_line_a)
        action = self._run_add_to_po(aml_row)
        new_po = self.env["purchase.order"].browse(action["res_id"])
        new_pol = new_po.order_line.filtered(
            lambda line: line.product_id == self.product_a
        )
        self.assertEqual(new_pol.product_qty, 2)
        self.assertEqual(new_pol.price_unit, 15.0)
        self.assertEqual(new_pol.product_uom, self.product_a.uom_id)
        self.assertEqual(new_pol.taxes_id, tax)

    def test_add_to_po_without_bill_line_raises(self):
        """Selecting only PO lines (no bill line) cannot Add to PO."""
        bill = self._draft_bill([self.product_a])
        po_row = self._pol_rows(self._match_rows(bill), self.po_line_a)
        with self.assertRaises(UserError):
            po_row.action_add_to_po()

    def test_add_to_po_no_downpayment_action(self):
        """The down-payment sub-case is not backported (no action exposed)."""
        self.assertFalse(
            hasattr(self.env["bill.to.po.wizard"], "action_add_downpayment"),
            "action_add_downpayment must not be backported (is_downpayment absent in 16.0 CE)",
        )
