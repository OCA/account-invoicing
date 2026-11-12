# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import new_test_user, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveTierValidationApprover(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.test_approver = new_test_user(
            cls.env,
            name="Approver",
            login="test2",
            groups="base.group_user,account.group_account_manager",
        )
        cls.res_partner_1 = cls.env["res.partner"].create(
            {
                "name": "Wood Corner",
                "email": "example@yourcompany.com",
                "approver_id": cls.test_approver.id,
            }
        )
        cls.product_1 = cls.env["product.product"].create({"name": "Desk Combination"})
        cls.currency_usd = cls.env["res.currency"].search(
            [("name", "=", "USD")], limit=1
        )
        cls.test_user_1 = new_test_user(
            cls.env,
            name="User",
            login="test1",
            groups="base.group_user,account.group_account_manager",
        )

        cls.vendor_bill = cls.env["account.move"].create(
            [
                {
                    "move_type": "in_invoice",
                    "partner_id": cls.res_partner_1.id,
                    "currency_id": cls.currency_usd.id,
                    "approver_id": cls.test_approver.id,
                    "invoice_line_ids": [
                        (
                            0,
                            None,
                            {
                                "product_id": cls.product_1.id,
                                "product_uom_id": cls.product_1.uom_id.id,
                                "quantity": 12,
                                "price_unit": 1000,
                            },
                        ),
                    ],
                }
            ]
        )
        cls.model_id = cls.env["ir.model"].search(
            [("model", "=", "account.move")], limit=1
        )
        cls.field_id = cls.env["ir.model.fields"].search(
            [("model", "=", "account.move"), ("name", "=", "approver_id")], limit=1
        )

    def test_01_field_validation_approver(self):
        """Test tier validation process with an approver."""
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
        record.with_user(self.test_user_1.id).validate_tier()
        with self.assertRaises(ValidationError):
            record.action_post()
        record.with_user(self.test_approver.id).validate_tier()
        record.action_post()

    def test_02_compute_approver_id(self):
        """Test that approver_id computes from partner_id."""
        # Test partner without approver
        partner_no_approver = self.env["res.partner"].create({"name": "No Approver"})
        move = self.env["account.move"].new(
            {
                "move_type": "in_invoice",
                "partner_id": partner_no_approver.id,
            }
        )
        self.assertFalse(move.approver_id)

        # Test partner with approver
        move.partner_id = self.res_partner_1
        self.assertEqual(move.approver_id, self.test_approver)

        # Test manual override
        other_user = self.test_user_1
        move.approver_id = other_user
        self.assertEqual(move.approver_id, other_user)
        # Check that it retains its value during compute trigger
        move._compute_approver_id()
        self.assertEqual(move.approver_id, other_user)

    def test_03_require_approver_config_and_post(self):
        """Test config setting and validation on post (coverage improvement)."""
        config = self.env["res.config.settings"].create(
            {
                "require_approver_in_vendor_bills": True,
            }
        )
        config.set_values()

        tier = self.env.company.validation_approver_tier_definition_id
        self.assertTrue(tier)
        self.assertTrue(tier.active)

        # Test disabling config
        config.require_approver_in_vendor_bills = False
        config.set_values()
        self.assertFalse(tier.active)

        # Enable again for posting test
        config.require_approver_in_vendor_bills = True
        config.set_values()

        # Create a move without approver
        partner = self.env["res.partner"].create({"name": "No Approver Partner"})
        move = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_date": "2020-01-01",
            }
        )
        self.assertFalse(move.approver_id)

        # Ensure UserError is raised on _post
        with self.assertRaisesRegex(
            UserError, "It is mandatory to indicate a Responsible for Approval"
        ):
            move._post()
