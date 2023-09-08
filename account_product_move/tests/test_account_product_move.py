# Copyright 2022-2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountProductMove(TransactionCase):
    def setUp(self):
        super().setUp()
        # Models used in tests.
        self.partner_model = self.env["res.partner"]
        self.product_template_model = self.env["product.template"]
        self.product_move_model = self.env["account.product.move"]
        self.product_move_line_model = self.env["account.product.move.line"]
        self.currency_model = self.env["res.currency"]
        self.rate_model = self.env["res.currency.rate"]
        # demo account.journals
        self.journal = self.env["account.journal"].create(
            {
                "name": "demo_journal",
                "type": "sale",
                "code": "code",
                "currency_id": self.env.company.currency_id.id,
            }
        )
        # a random product template
        self.product_template_01 = self.product_template_model.search(
            [("product_variant_ids", "!=", False)], limit=1
        )
        self.product = self.product_template_01.product_variant_ids[0]
        # a random demo account
        self.account = self.env["account.account"].search([], limit=1)
        # For succesfull test on non-empty database, archive existing moves.
        # This will automatically be undone by the end of the test.
        self.product_move_model.search([]).action_archive()
        # demo account product move
        self.product_move_01 = self.product_move_model.create(
            {
                "name": "TEST account_product_move",
                "journal_id": self.journal.id,
                "product_tmpl_ids": [(6, 0, self.product_template_01.ids)],
            }
        )
        # demo journal item lines for account product move
        self.item_line_01 = self.product_move_line_model.create(
            {
                "account_id": self.account.id,
                "move_id": self.product_move_01.id,
                "credit": 1.0,
            }
        )
        self.item_line_02 = self.product_move_line_model.create(
            {
                "account_id": self.account.id,
                "move_id": self.product_move_01.id,
                "debit": 1.0,
            }
        )
        self.item_line_03 = self.product_move_line_model.create(
            {
                "account_id": self.account.id,
                "move_id": self.product_move_01.id,
                "credit": 1.0,
            }
        )
        self.item_line_04 = self.product_move_line_model.create(
            {
                "account_id": self.account.id,
                "move_id": self.product_move_01.id,
                "debit": 1.0,
            }
        )
        self.product_move_01.button_complete()
        # demo invoice
        self.partner_01 = self.partner_model.search(
            [("customer_rank", ">", 0)], limit=1
        )
        self.invoice = self._make_invoice()

    def test_debit_credit_balance(self):
        """Check that balance is always 0 for template"""
        # First set to state new.
        self.product_move_01.button_reset()
        # Add unbalanced line.
        line = self.product_move_line_model.create(
            {
                "move_id": self.product_move_01.id,
                "credit": 1.0,
                "account_id": self.account.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.product_move_01.button_complete()
        # Remove line again and try again to complete.
        line.unlink()
        self.product_move_01.button_complete()
        # Create and complete move without lines. This should not be accepted.
        empty_move = self.product_move_model.create(
            {
                "name": "TEST empty account_product_move",
                "journal_id": self.journal.id,
                "product_tmpl_ids": [(6, 0, self.product_template_01.ids)],
            }
        )
        with self.assertRaises(ValidationError):
            empty_move.button_complete()
        # Try what happens when having unbalanced percentage lines.
        percentage_move = self.product_move_model.create(
            {
                "name": "TEST account_product_move with unblanced percentages",
                "journal_id": self.journal.id,
                "product_tmpl_ids": [(6, 0, self.product_template_01.ids)],
            }
        )
        self.product_move_line_model.create(
            {
                "account_id": self.account.id,
                "move_id": percentage_move.id,
                "percentage_credit": 5.0,
            }
        )
        debit_percentage_line = self.product_move_line_model.create(
            {
                "account_id": self.account.id,
                "move_id": percentage_move.id,
                "percentage_debit": 10.0,
            }
        )
        with self.assertRaises(ValidationError):
            percentage_move.button_complete()
        # Correcting the percentage should make it possible to complete.
        debit_percentage_line.write({"percentage_debit": 5.0})
        percentage_move.button_complete()

    def test_workflow(self):
        """Post invoice, set back to draft, etc. and check what happens."""
        # Post the invoice
        self.invoice.action_post()
        # Journal entries created
        self.assertTrue(self.invoice.product_move_ids)
        # Action returns these only
        self.assertEqual(
            self.invoice.product_move_ids,
            self.invoice.search(self.invoice.action_view_journal_entries()["domain"]),
        )
        # Product templates are the same
        self.assertEqual(
            self.invoice.mapped("line_ids.product_id.product_tmpl_id"),
            self.product_move_01.mapped("product_tmpl_ids"),
        )
        # Journals are the same
        self.assertEqual(
            self.invoice.mapped("product_move_ids.journal_id"),
            self.product_move_01.journal_id,
        )
        # Set invoice to draft
        self.invoice.button_draft()
        # See that all journal entries are in draft
        for this in self.invoice.product_move_ids:
            self.assertEqual(this.state, "draft")
        # Post again...
        self.invoice.action_post()
        # ...only to cancel right away
        self.invoice.button_cancel()
        for this in self.invoice.product_move_ids:
            self.assertEqual(this.state, "cancel")

    def test_filter(self):
        """Test creation of extra moves (or non creation) depending on filter."""
        invoice = self._make_invoice()
        filter_model = self.env["ir.filters"]
        partner_filter = filter_model.create(
            {
                "name": "Invoices for Bond 007",
                "domain": "[('partner_id.name', '=', 'Bond 007')]",
                "model_id": "account.move",
                "user_id": False,
            }
        )
        # Link filter to model.
        self.product_move_01.write({"filter_id": partner_filter.id})
        # Post the invoice.
        invoice.action_post()
        # No journal entries should have been created.
        self.assertFalse(invoice.product_move_ids)
        # Change filter and try again.
        partner_filter.write(
            {"domain": "[('partner_id.name', '=', '%s')]" % self.partner_01.name}
        )
        invoice.button_draft()
        invoice.action_post()
        self.assertTrue(invoice.product_move_ids)
        # Filter with empty domain is also valid.
        partner_filter.write({"domain": "[]"})
        invoice.button_draft()
        invoice.action_post()
        self.assertTrue(invoice.product_move_ids)

    def test_is_product_move_valid(self):
        """Test the non filter part of is_product_move_valid."""
        invoice_line = self.invoice.line_ids[0]
        # Move as is is valid.
        self.assertTrue(invoice_line._is_product_move_valid(self.product_move_01))
        # Not complete move is not valid.
        self.product_move_01.button_reset()
        self.assertFalse(invoice_line._is_product_move_valid(self.product_move_01))
        self.product_move_01.button_complete()

    def test_foreign_currency(self):
        """Test with a currency that has twice the value of company currency."""
        strubl = self._make_foreign_currency()
        strubl_move = self.product_move_model.create(
            {
                "name": "TEST account_product_move with foreign currency",
                "journal_id": self.journal.id,
                "product_tmpl_ids": [(6, 0, self.product_template_01.ids)],
            }
        )
        self.product_move_line_model.create(
            {
                "account_id": self.account.id,
                "move_id": strubl_move.id,
                "currency_id": strubl.id,
                "credit": 10.0,
            }
        )
        self.product_move_line_model.create(
            {
                "account_id": self.account.id,
                "move_id": strubl_move.id,
                "currency_id": strubl.id,
                "debit": 10.0,
            }
        )
        # Deactivate standard apm and activate strubl apm.
        self.product_move_01.button_reset()
        strubl_move.button_complete()
        # Post the invoice
        self.invoice.action_post()
        # Journal entries created
        self.assertTrue(self.invoice.product_move_ids)
        # Action returns these only
        self.assertEqual(
            self.invoice.product_move_ids,
            self.invoice.search(self.invoice.action_view_journal_entries()["domain"]),
        )
        # Check the moves created.
        extra_move = self.invoice.product_move_ids
        self.assertEqual(len(extra_move), 1)  # There can be only one.
        # Get conversion rate of company curreny to strubl.
        company = self.env.company
        conversion_rate = self.currency_model._get_conversion_rate(
            strubl, company.currency_id, company, fields.Date.today()
        )
        for extra_line in extra_move.line_ids:
            self.assertEqual(extra_line.currency_id, strubl)
            if extra_line.debit:
                expected_amount = extra_line.amount_currency * conversion_rate
                compare_amount = extra_line.debit
            else:
                expected_amount = 0.0 - (extra_line.amount_currency * conversion_rate)
                compare_amount = extra_line.credit
            self.assertEqual(
                0, company.currency_id.compare_amounts(compare_amount, expected_amount)
            )

    def test_constraints(self):
        """Check several constraints."""
        self.product_move_01.button_reset()  # Should not edit with state complete.
        # Should not mix debit and credit
        with self.assertRaises(ValidationError):
            self.product_move_line_model.create(
                {
                    "move_id": self.product_move_01.id,
                    "credit": 1.0,
                    "percentage_debit": 1.0,
                    "account_id": self.account.id,
                }
            )
        # Should not use percentage with foreign currency.
        strubl = self._make_foreign_currency()
        with self.assertRaises(ValidationError):
            self.product_move_line_model.create(
                {
                    "move_id": self.product_move_01.id,
                    "percentage_debit": 1.0,
                    "account_id": self.account.id,
                    "currency_id": strubl.id,
                }
            )

    def test_percentage(self):
        """Test creating moves with percentage of standard_price (cost)."""
        self.product_move_01.button_reset()  # Should not edit with state complete.
        for line in self.product_move_01.line_ids:
            if line.debit:
                line.write({"debit": 0.0, "percentage_debit": 10.0})
            if line.credit:
                line.write({"credit": 0.0, "percentage_credit": 10.0})
        self.product_move_01.button_complete()
        self.product.standard_price = 50.0  # in company currency
        expected_amount = 300.0 * 10.0 * 0.01 * 50.0
        # Post the invoice
        self.invoice.action_post()
        # Check the moves created.
        extra_move = self.invoice.product_move_ids
        self.assertEqual(len(extra_move), 1)  # There can be only one.
        self.assertEqual(len(extra_move.line_ids), 4)
        for extra_line in extra_move.line_ids:
            if extra_line.debit:
                self.assertEqual(extra_line.debit, expected_amount)
            if extra_line.credit:
                self.assertEqual(extra_line.credit, expected_amount)

    def _make_invoice(self):
        """Make fresh invoice for each test."""
        invoice = self.env["account.move"].create(
            {
                "type": "out_invoice",
                "date": fields.Date.today(),
                "partner_id": self.partner_01.id,
                "line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": self.product.id,
                            "quantity": 300.0,
                            "account_id": self.account.id,
                        },
                    ),
                ],
            }
        )
        return invoice

    def _make_foreign_currency(self):
        """Return non company currency for testing."""
        strubl = self.currency_model.create(
            {
                "name": "STRUBL",  # The national currency of Molvania
                "symbol": "₰",
                "active": True,
            }
        )
        self.rate_model.create(
            {"currency_id": strubl.id, "name": "2001-01-01", "rate": 0.5}
        )
        return strubl
