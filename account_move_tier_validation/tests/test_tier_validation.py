# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import new_test_user, tagged

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
        self.env["tier.definition"].create(
            {
                "model_id": self.account_move_model.id,
                "definition_domain": "[('move_type', '=', 'out_invoice')]",
                "reviewer_id": self.test_user_1.id,
            }
        )
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        product = self.env["product.product"].create({"name": "Test product"})
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_date_due": fields.Date.to_date("2024-01-01"),
                "invoice_line_ids": [
                    Command.create(
                        {"product_id": product.id, "quantity": 1, "price_unit": 30}
                    )
                ],
            }
        )
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
