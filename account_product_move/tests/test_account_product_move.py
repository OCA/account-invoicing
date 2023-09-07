# Copyright 2022-2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountProductMove(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_model = self.env["res.partner"]
        self.product_template_model = self.env["product.template"]
        self.product_move_model = self.env["account.product.move"]
        self.product_move_line_model = self.env["account.product.move.line"]
        # demo account.journals
        self.journal = self.env["account.journal"].create(
            {"name": "demo_journal", "type": "sale", "code": "code"}
        )
        self.another_journal = self.env["account.journal"].create(
            {"name": "another_demo_journal", "type": "sale", "code": "code"}
        )
        # a random product template
        self.product_template_01 = self.product_template_model.search(
            [("product_variant_ids", "!=", False)], limit=1
        )
        self.product = self.product_template_01.product_variant_ids[0]
        # a random demo account
        self.account = self.env["account.account"].search([], limit=1)
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
        self.invoice = self.env["account.move"].create(
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
            # Try to set state to complete.
            self.product_move_01.button_complete()
        # Remove line again and try again to complete.
        line.unlink()
        self.product_move_01.button_complete()

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
        self.invoice.action_post()
        # No journal entries should have been created.
        self.assertFalse(self.invoice.product_move_ids)
        # Change filter and try again.
        partner_filter.write(
            {"domain": "[('partner_id.name', '=', '%s')]" % self.partner_01.name}
        )
        self.invoice.button_draft()
        self.invoice.action_post()
        self.assertTrue(self.invoice.product_move_ids)
