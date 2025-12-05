# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestAccountBillingPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.portal_partner = cls.env["res.partner"].create(
            {
                "name": "Portal Partner",
                "email": "portal.partner@example.com",
            }
        )
        cls.portal_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Portal User",
                    "login": "portal_user",
                    "password": "portal_user",
                    "email": "portal_user@example.com",
                    "partner_id": cls.portal_partner.id,
                    "groups_id": [Command.set([cls.env.ref("base.group_portal").id])],
                    "company_id": cls.company.id,
                    "company_ids": [Command.set([cls.company.id])],
                }
            )
        )
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.account_revenue = cls.env["account.account"].search(
            [
                ("account_type", "=", "income"),
                ("company_ids", "=", cls.company.id),
            ],
            limit=1,
        )
        inv1 = cls._create_posted_invoice(partner_id=cls.portal_partner.id, amount=100)
        inv2 = cls._create_posted_invoice(partner_id=cls.portal_partner.id, amount=200)
        action = (inv1 + inv2).action_create_billing()
        cls.portal_billing = cls.env["account.billing"].browse(action["res_id"])
        cls.portal_billing.validate_billing()
        cls.other_partner = cls.env["res.partner"].create(
            {
                "name": "Other Partner",
                "email": "other.partner@example.com",
            }
        )
        inv3 = cls._create_posted_invoice(partner_id=cls.other_partner.id, amount=123)
        action2 = inv3.action_create_billing()
        cls.other_billing = cls.env["account.billing"].browse(action2["res_id"])
        cls.other_billing.validate_billing()

    @classmethod
    def _create_posted_invoice(cls, partner_id, amount, move_type="out_invoice"):
        move = cls.env["account.move"].create(
            {
                "partner_id": partner_id,
                "move_type": move_type,
                "invoice_date": fields.Date.context_today(cls.env.user),
                "date": fields.Date.context_today(cls.env.user),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Test line",
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "price_unit": amount,
                            "account_id": cls.account_revenue.id,
                        }
                    )
                ],
            }
        )
        move.action_post()
        return move

    def test_portal_billings_list_renders(self):
        self.authenticate(self.portal_user.login, "portal_user")
        res = self.url_open("/my/billings")
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.portal_billing.name, res.text)

    def test_portal_billing_detail_renders(self):
        self.authenticate(self.portal_user.login, "portal_user")
        res = self.url_open(f"/my/billings/{self.portal_billing.id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.portal_billing.name, res.text)

    def test_portal_billing_detail_redirects_when_not_allowed(self):
        self.authenticate(self.portal_user.login, "portal_user")
        res = self.url_open(
            f"/my/billings/{self.other_billing.id}", allow_redirects=False
        )
        self.assertNotEqual(res.status_code, 200)
        self.assertTrue(res.headers.get("Location", "").endswith("/my"))

    def test_action_billing_send(self):
        result = self.portal_billing.action_billing_send()
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "mail.compose.message")
        self.assertEqual(result["target"], "new")
        # Check that a PDF attachment was created and linked in context
        ctx = result["context"]
        attach_ids = ctx["default_attachment_ids"][0][2]
        attachment = self.env["ir.attachment"].browse(attach_ids[0])
        self.assertTrue(attachment)
