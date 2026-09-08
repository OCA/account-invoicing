# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import new_test_user, tagged, users
from odoo.tools.misc import mute_logger

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountTierValidation(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Disable logs to prevent logs from obscuring test results
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # AccountTestInvoicingCommon already loads the chart of accounts and
        # creates sale/purchase/bank journals, so no extra journal setup is needed here.

        # Configure the company's external report layout so that
        # action_invoice_sent() opens account.move.send.wizard directly.
        # Without this, Odoo first asks the user to set up the document layout
        # and returns a base.document.layout action instead of the send wizard.
        if not cls.env.company.external_report_layout_id:
            # Try the standard web layout first (an ir.ui.view record)
            layout_view = cls.env.ref(
                "web.external_layout_standard", raise_if_not_found=False
            )
            if not layout_view:
                # Fall back to any report.layout whose view_id we can use
                # (only reached if web.external_layout_standard is absent)
                report_layout = cls.env["report.layout"].search([], limit=1)
                layout_view = report_layout.view_id if report_layout else None
            if layout_view:
                cls.env.company.external_report_layout_id = layout_view

        cls.group_system = cls.env.ref("base.group_system")
        cls.group_account_manager = cls.env.ref("account.group_account_manager")
        cls.test_user_1 = new_test_user(
            cls.env,
            name="John",
            login="test1",
            groups="base.group_system,account.group_account_manager",
        )
        cls.test_user_2 = new_test_user(
            cls.env,
            name="Mike",
            login="test2",
            groups="base.group_system,account.group_account_manager",
        )
        cls.test_user_3 = new_test_user(
            cls.env,
            name="Nolan",
            login="test3",
            groups="account.group_account_user",
        )
        # Partner must have an email address; without it action_send_and_print()
        # raises UserError("Partner(s) should have an email address.")
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "email": "test.partner@example.com"}
        )
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.account_move_model = cls.env["ir.model"]._get("account.move")

    def _prepare_tier_definition(self, sudo_flag=False, move_type="out_invoice"):
        return (
            self.env["tier.definition"]
            .sudo(flag=sudo_flag)
            .create(
                {
                    "model_id": self.account_move_model.id,
                    "definition_domain": f"[('move_type', '=', '{move_type}')]",
                    "reviewer_id": self.test_user_1.id,
                }
            )
        )

    def _prepare_move(self, sudo_flag=False, move_type="out_invoice"):
        return (
            self.env["account.move"]
            .sudo(flag=sudo_flag)
            .create(
                {
                    "move_type": move_type,
                    "partner_id": self.partner.id,
                    "invoice_date_due": fields.Date.to_date("2024-01-01"),
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "product_id": self.product.id,
                                "quantity": 1,
                                "price_unit": 30,
                            }
                        )
                    ],
                }
            )
        )

    def test_01_tier_definition_models(self):
        """account.move must be registered as a tier-validation model."""
        res = self.env["tier.definition"]._get_tier_validation_model_names()
        self.assertIn("account.move", res)

    def test_02_form(self):
        """hide_post_button must be True when a tier definition applies to the move."""
        for move_type in ("in_invoice", "out_invoice", "in_refund", "out_refund"):
            self.env["tier.definition"].create(
                {
                    "model_id": self.account_move_model.id,
                    "definition_domain": f"[('move_type', '=', '{move_type}')]",
                }
            )
            with Form(
                self.env["account.move"].with_context(default_move_type=move_type)
            ) as form:
                form.save()
                self.assertTrue(form.hide_post_button)

    def test_03_move_post(self):
        """Full validation workflow: request → validate → post → send by email."""
        self._prepare_tier_definition()
        invoice = self._prepare_move()
        invoice.with_user(self.test_user_2.id).request_validation()
        invoice = invoice.with_user(self.test_user_1.id)
        invoice.invalidate_model()
        invoice.validate_tier()
        with self.assertRaisesRegex(
            ValidationError, "You are not allowed to write those fields"
        ):
            invoice._post()
        # action_post() injects skip_validation_check=True via our override in
        # AccountMove.action_post(), so this must succeed.
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

        # --- Simulate Sending Invoice by Email ---
        # The 'action_invoice_sent' method on 'account.move' usually returns
        # an action to open the 'account.move.send.wizard' wizard.
        action = invoice.action_invoice_sent()
        self.assertTrue(
            action, "Action 'action_invoice_sent' should return an action dictionary."
        )
        self.assertEqual(
            action.get("res_model"),
            "account.move.send.wizard",
            "Action should open 'account.move.send.wizard' wizard.",
        )

        # Get the context from the action to create the wizard instance
        wizard_context = action.get("context", {})
        mail_composer = (
            self.env["account.move.send.wizard"]
            .with_context(**wizard_context)
            .create({})
        )

        # we should test action_send_and_print because that fails if
        # not all necessary fields are excluded
        mail_composer.action_send_and_print()

    @users("test3")
    def test_04_move_reset_to_draft(self):
        """Test we can revert a posted move back to draft (reviews are dropped)."""
        self._prepare_tier_definition(sudo_flag=True, move_type="in_invoice")
        # User 3 creates the vendor bill
        vendor_bill = self._prepare_move(move_type="in_invoice")
        # User 3 adds the invoice date (else the posting action fails), but it does it
        # before requesting validation (else the update itself fails)
        vendor_bill.invoice_date = fields.Date.context_today(vendor_bill)
        self.assertEqual(len(vendor_bill.review_ids), 0)
        self.assertEqual(vendor_bill.validation_status, "no")
        # User 3 requires validation for the bill
        vendor_bill.request_validation()
        self.assertEqual(len(vendor_bill.review_ids), 1)
        self.assertEqual(vendor_bill.review_ids.status, "pending")
        self.assertEqual(vendor_bill.validation_status, "pending")
        # User 1 validates it
        vendor_bill.with_user(self.test_user_1.id).validate_tier()
        self.assertEqual(len(vendor_bill.review_ids), 1)
        self.assertEqual(vendor_bill.review_ids.status, "approved")
        self.assertEqual(vendor_bill.validation_status, "validated")
        # Invalidate model to force Odoo to recompute field ``need_validation``: it is a
        # computed, non-stored field, but its compute method has no ``@api.depends``
        # decorator and its value is checked upon calling ``write()`` (which is
        # called by ``action_post()`` to update the vendor bill's status)
        vendor_bill.invalidate_model()
        # User 3 posts the vendor bill
        vendor_bill.action_post()
        self.assertEqual(vendor_bill.state, "posted")
        self.assertEqual(len(vendor_bill.review_ids), 1)
        self.assertEqual(vendor_bill.review_ids.status, "approved")
        self.assertEqual(vendor_bill.validation_status, "validated")
        # User 3 reverts the vendor bill to draft; button_draft() must delete
        # existing reviews so that tier_validation doesn't block the status write.
        with mute_logger("odoo.models.unlink"):
            vendor_bill.button_draft()
        self.assertEqual(vendor_bill.state, "draft")
        self.assertEqual(len(vendor_bill.review_ids), 0)
        self.assertEqual(vendor_bill.validation_status, "no")

    def test_05_get_to_validate_message_name(self):
        """Cover all four move_type branches of _get_to_validate_message_name().

        Lines 44-54 of account_move.py were not executed because none of the
        existing tests actually inspected the method's return value across all
        move types.  This test calls the method directly for each type so that
        every branch is covered.
        """
        expected = {
            "in_invoice": "Bill",
            "in_refund": "Refund",
            "out_invoice": "Invoice",
            "out_refund": "Credit Note",
        }
        for move_type, label in expected.items():
            move = self.env["account.move"].new({"move_type": move_type})
            result = move._get_to_validate_message_name()
            self.assertEqual(
                result,
                label,
                f"Expected '{label}' for move_type '{move_type}', got '{result}'",
            )

    def test_06_get_under_validation_exceptions(self):
        """Cover _get_under_validation_exceptions() (line 23 of account_move.py).

        The method adds 'needed_terms_dirty' to the base exception list so that
        edits on payment-terms lines don't trigger write-protection errors during
        validation.  We verify that the field is present in the returned list.
        """
        move = self.env["account.move"].new({"move_type": "out_invoice"})
        exceptions = move._get_under_validation_exceptions()
        self.assertIn(
            "needed_terms_dirty",
            exceptions,
            "'needed_terms_dirty' must be an under-validation"
            " exception for account.move",
        )
