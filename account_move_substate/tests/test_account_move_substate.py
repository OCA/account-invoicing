# Copyright 2023 bosd (<bosd>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseSubstate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.substate_test_account_move = self.env["account.move"]
        self.substate_test_account_move_line = self.env["account.move.line"]

        # Create substate type for account.move
        self.substate_type = self.env["base.substate.type"].create(
            {
                "name": "Account Move Substate",
                "model": "account.move",
                "target_state_field": "state",
            }
        )

        # Create target state values
        self.target_state_draft = self.env["target.state.value"].create(
            {
                "name": "Draft",
                "base_substate_type_id": self.substate_type.id,
                "target_state_value": "draft",
            }
        )

        self.target_state_posted = self.env["target.state.value"].create(
            {
                "name": "Posted",
                "base_substate_type_id": self.substate_type.id,
                "target_state_value": "posted",
            }
        )

        # Create substates
        self.substate_to_verify = self.env["base.substate"].create(
            {
                "name": "To Verify",
                "sequence": 1,
                "target_state_value_id": self.target_state_draft.id,
            }
        )

        self.substate_checked = self.env["base.substate"].create(
            {
                "name": "Checked",
                "sequence": 2,
                "target_state_value_id": self.target_state_draft.id,
            }
        )

        self.substate_verified = self.env["base.substate"].create(
            {
                "name": "Verified",
                "sequence": 3,
                "target_state_value_id": self.target_state_posted.id,
            }
        )

        self.product = self.env["product.product"].create({"name": "Test"})

    def test_account_move_substate_basic(self):
        """Test basic substate functionality with invoice"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner 12",
                "email": "testpartner12@example.com",
            }
        )
        invoice = self.substate_test_account_move.create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "quantity": 1,
                            "price_unit": 450,
                            "tax_ids": [(6, 0, [])],
                        },
                    )
                ],
            }
        )

        self.assertTrue(invoice.state == "draft")

        # Try to assign a posted-only substate to a draft invoice (should raise error)
        with self.assertRaises(ValidationError):
            invoice.substate_id = self.substate_verified

        # Assign a draft-compatible substate
        invoice.substate_id = self.substate_to_verify.id
        self.assertEqual(invoice.substate_id, self.substate_to_verify)

        # Post the invoice
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

        # After posting, we can assign a posted-compatible substate
        invoice.substate_id = self.substate_verified.id
        self.assertEqual(invoice.substate_id, self.substate_verified)

        # test that there is no substate id after cancellation
        invoice.button_cancel()
        self.assertTrue(invoice.state == "cancel")
        self.assertTrue(not invoice.substate_id)

    def test_account_move_substate_with_different_states(self):
        """Test substate assignment with different account move states"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner Different",
                "email": "testpartnerdiff@example.com",
            }
        )
        receivable_account = self.env["account.account"].search(
            [
                ("account_type", "=", "asset_receivable"),
            ],
            limit=1,
        )
        payable_account = self.env["account.account"].search(
            [
                ("account_type", "=", "liability_payable"),
            ],
            limit=1,
        )

        if not receivable_account or not payable_account:
            # Fallback to any existing accounts if standard ones aren't found
            receivable_account = self.env["account.account"].search([], limit=1)
            payable_account = self.env["account.account"].search([], limit=1)

        if receivable_account and payable_account:
            move = self.substate_test_account_move.create(
                {
                    "move_type": "entry",  # journal entry
                    "partner_id": partner.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Debit line",
                                "debit": 100,
                                "credit": 0,
                                "account_id": receivable_account.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Credit line",
                                "debit": 0,
                                "credit": 100,
                                "account_id": payable_account.id,
                            },
                        ),
                    ],
                }
            )

            # Assign a draft-compatible substate
            move.substate_id = self.substate_to_verify.id
            self.assertEqual(move.substate_id, self.substate_to_verify)

            # Post the move - should allow substate with posted state
            move.action_post()
            self.assertEqual(move.state, "posted")
        else:
            # Skip this test if accounts are not available
            pass

    def test_substate_validation_on_state_change(self):
        """Test that substate validation occurs properly during state changes"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner Validation",
                "email": "testpartnerval@example.com",
            }
        )
        move = self.substate_test_account_move.create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

        # Assign a draft-compatible substate
        move.substate_id = self.substate_to_verify.id
        self.assertEqual(move.substate_id, self.substate_to_verify)

        # Try to assign a posted-only substate to a draft move (should raise error)
        with self.assertRaises(ValidationError):
            move.substate_id = self.substate_verified.id

    def test_substate_clearance_on_cancellation(self):
        """Test that substate is cleared when moving to cancel state"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner Cancellation",
                "email": "testpartnercancel@example.com",
            }
        )
        move = self.substate_test_account_move.create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

        # Post the move first
        move.action_post()

        # Assign a posted-compatible substate
        move.substate_id = self.substate_verified.id
        self.assertEqual(move.substate_id, self.substate_verified)

        # Cancel the move - substate should be cleared
        move.button_cancel()
        self.assertEqual(move.state, "cancel")
        self.assertFalse(move.substate_id)

    def test_multiple_substate_assignments(self):
        """Test assigning different substates during the lifecycle of an account move"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner Multiple",
                "email": "testpartnermulti@example.com",
            }
        )
        move = self.substate_test_account_move.create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

        # Initially in draft, assign draft-compatible substate
        move.substate_id = self.substate_to_verify.id
        self.assertEqual(move.substate_id, self.substate_to_verify)

        # Change to another draft-compatible substate
        move.substate_id = self.substate_checked.id
        self.assertEqual(move.substate_id, self.substate_checked)

        # Post the move
        move.action_post()
        self.assertEqual(move.state, "posted")

        # Now assign a posted-compatible substate
        move.substate_id = self.substate_verified.id
        self.assertEqual(move.substate_id, self.substate_verified)
