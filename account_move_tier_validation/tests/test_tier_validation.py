# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import new_test_user, tagged, users
from odoo.tools.misc import mute_logger

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestAccountTierValidation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.account_move_model = cls.env["ir.model"]._get("account.move")

        # Ensure the company has a document layout configured.
        if not cls.company.external_report_layout_id:
            # Try to find a common default layout by XML ID
            default_layout = cls.env.ref(
                "web.external_layout_standard", raise_if_not_found=False
            )
            if not default_layout:
                # Fallback: try other common layouts if standard
                # is not found by that XML ID directly
                common_layouts_xml_ids = [
                    "web.external_layout_boxed",
                    "web.external_layout_bold",
                ]
                for layout_xml_id in common_layouts_xml_ids:
                    default_layout = cls.env.ref(
                        layout_xml_id, raise_if_not_found=False
                    )
                    if default_layout:
                        break
            if not default_layout:
                # As a last resort, find the first available report.layout
                default_layout = cls.env["report.layout"].search([], limit=1)

            if default_layout:
                cls.company.external_report_layout_id = default_layout.id

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
        res = self.env["tier.definition"]._get_tier_validation_model_names()
        self.assertIn("account.move", res)

    def test_02_form(self):
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
        # Calls _post method by passing context skip_validation_check set to True
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
        # not all necesary fields are excluded
        if hasattr(mail_composer, "action_send_and_print"):
            mail_composer.action_send_and_print()
        else:
            self.fail(
                "Could not find a 'action_send_and_print' "
                "action on the account.move.send.wizard."
            )

    @users("test3")
    def test_04_move_reset_to_draft(self):
        """Test we can revert a posted move back to draft"""
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
        self.assertEqual(vendor_bill.review_ids.status, "waiting")
        self.assertEqual(vendor_bill.validation_status, "waiting")
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
        # User 3 reverts the vendor bill to draft
        with mute_logger("odoo.models.unlink"):
            vendor_bill.button_draft()
        self.assertEqual(vendor_bill.state, "draft")
        self.assertEqual(len(vendor_bill.review_ids), 0)
        self.assertEqual(vendor_bill.validation_status, "no")
