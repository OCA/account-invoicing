# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields
from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tests.common import tagged


@tagged("post_install", "-at_install")
class TestAccountTierValidation(common.TransactionCase):
    def test_01_tier_definition_models(self):
        res = self.env["tier.definition"]._get_tier_validation_model_names()
        self.assertIn("account.move", res)

    def test_02_form(self):
        for _type in ("in_invoice", "out_invoice", "in_refund", "out_refund"):
            self.env["tier.definition"].create(
                {
                    "model_id": self.env["ir.model"]
                    .search([("model", "=", "account.move")])
                    .id,
                    "definition_domain": "[('move_type', '=', '%s')]" % _type,
                }
            )
            with common.Form(
                self.env["account.move"].with_context(default_move_type=_type)
            ) as form:
                form.save()
                self.assertTrue(form.hide_post_button)

    def test_03_move_post(self):
        group_ids = [
            self.env.ref("base.group_system").id,
            self.env.ref("account.group_account_manager").id,
        ]
        self.test_user_1 = self.env["res.users"].create(
            {
                "name": "John",
                "login": "test1",
                "email": "john@test.com",
                "groups_id": [(6, 0, group_ids)],
            }
        )
        self.test_user_2 = self.env["res.users"].create(
            {
                "name": "Mike",
                "login": "test2",
                "email": "mike@test.com",
                "groups_id": [(6, 0, group_ids)],
            }
        )
        self.env["tier.definition"].create(
            {
                "model_id": self.env["ir.model"]
                .search([("model", "=", "account.move")])
                .id,
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
                "invoice_date_due": fields.Date.from_string("2024-01-01"),
                "invoice_line_ids": [
                    (0, 0, {"product_id": product.id, "quantity": 1, "price_unit": 30})
                ],
            }
        )
        invoice.with_user(self.test_user_2.id).request_validation()
        invoice = invoice.with_user(self.test_user_1.id)
        invoice.invalidate_model()
        invoice.validate_tier()
        with self.assertRaisesRegex(
            ValidationError, _("You are not allowed to write those fields")
        ):
            invoice._post()
        # Calls _post method by passing context skip_validation_check set to True
        invoice.action_post()
