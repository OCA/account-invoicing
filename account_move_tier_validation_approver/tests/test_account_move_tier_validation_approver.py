# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountMoveTierValidationApprover(TransactionCase):
    def setUp(self):
        super(TestAccountMoveTierValidationApprover, self).setUp()
        self.res_partner_1 = self.env["res.partner"].create(
            {"name": "Wood Corner", "email": "example@yourcompany.com"}
        )
        self.product_1 = self.env["product.product"].create(
            {"name": "Desk Combination"}
        )
        self.currency_euro = self.env["res.currency"].search([("name", "=", "EUR")])
        self.test_user_1 = self.env["res.users"].create(
            {"name": "User", "login": "test1", "email": "example@yourcompany.com"}
        )
        self.test_approver = self.env["res.users"].create(
            {"name": "Approver", "login": "test2", "email": "example@yourcompany.com"}
        )
        self.vendor_bill = self.env["account.move"].create(
            [
                {
                    "move_type": "in_invoice",
                    "partner_id": self.res_partner_1.id,
                    "currency_id": self.currency_euro.id,
                    "approver_id": self.test_approver.id,
                    "invoice_line_ids": [
                        (
                            0,
                            None,
                            {
                                "product_id": self.product_1.id,
                                "product_uom_id": self.product_1.uom_id.id,
                                "quantity": 12,
                                "price_unit": 1000,
                            },
                        ),
                    ],
                }
            ]
        )
        self.model_id = self.env["ir.model"].search(
            [("model", "=", "account.move")], limit=1
        )
        self.field_id = self.env["ir.model.fields"].search(
            [("name", "=", "approver_id")], limit=1
        )

    def test_field_validation_approver(self):
        tiers = self.env["tier.definition"].search([])
        for tier in tiers:
            tier.action_archive()
        self.tier_definition = self.env["tier.definition"].create(
            {
                "name": "Test Tier",
                "model_id": self.model_id.id,
                "review_type": "field",
                "reviewer_field_id": self.field_id.id,
                "definition_type": "domain",
                "definition_domain": "[('move_type', '=', 'in_invoice')]",
            }
        )
        record = self.vendor_bill
        record.write(
            {"approver_id": self.test_approver.id, "invoice_date": record.date}
        )
        record.with_user(self.test_user_1.id).request_validation()
        record.invalidate_cache()
        record.with_user(self.test_user_1.id).validate_tier()
        with self.assertRaises(ValidationError):
            record.action_post()
        record.with_user(self.test_approver.id).validate_tier()
        record.action_post()
