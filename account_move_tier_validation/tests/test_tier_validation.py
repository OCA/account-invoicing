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
