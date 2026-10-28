# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from odoo import Command
from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPartnerAccess(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_portal = cls.env.ref("base.group_portal")
        cls.user_a = cls._create_user(cls, "A")
        cls.user_b = cls._create_user(cls, "B")
        cls.user_c = cls._create_user(cls, "C")
        cls.partner_a = cls._create_partner(cls, cls.user_a)
        cls.partner_b = cls._create_partner(cls, cls.user_b)
        cls.partner_c = cls._create_partner(cls, cls.user_c)
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "product_a",
                "lst_price": 1000.0,
                "standard_price": 800.0,
            }
        )

    def _create_user(self, letter):
        return self.env["res.users"].create(
            {
                "name": f"User {letter}",
                "login": f"user_{letter}",
                "group_ids": [Command.set([self.group_portal.id])],
            }
        )

    def _create_partner(self, user):
        return self.env["res.partner"].create(
            {
                "name": user.name,
                "user_ids": [Command.set([user.id])],
            }
        )

    def _create_portal_invoice(self, partner, post=True):
        return self.init_invoice(
            "out_invoice", partner=partner, post=post, products=self.product_a
        )

    def test_access_invoice(self):
        invoice_a = self._create_portal_invoice(self.partner_a)
        invoice_b = self._create_portal_invoice(self.partner_b)
        invoice_c = self._create_portal_invoice(self.partner_c)
        # Access is granted as the invoice partner, with no need to be a follower
        self.assertNotIn(self.partner_a, invoice_a.message_partner_ids)
        found_a = self.env["account.move"].with_user(self.user_a).search([])
        self.assertIn(invoice_a, found_a)
        self.assertNotIn(invoice_b, found_a)
        self.assertNotIn(invoice_c, found_a)
        found_b = self.env["account.move"].with_user(self.user_b).search([])
        self.assertNotIn(invoice_a, found_b)
        self.assertIn(invoice_b, found_b)
        self.assertNotIn(invoice_c, found_b)
        found_c = self.env["account.move"].with_user(self.user_c).search([])
        self.assertNotIn(invoice_a, found_c)
        self.assertNotIn(invoice_b, found_c)
        self.assertIn(invoice_c, found_c)

    def test_access_invoice_followers(self):
        # Being a follower grants access in addition to being the invoice partner
        invoice_a = self._create_portal_invoice(self.partner_a)
        found_b = self.env["account.move"].with_user(self.user_b).search([])
        self.assertNotIn(invoice_a, found_b)
        invoice_a.message_subscribe(partner_ids=self.partner_b.ids)
        found_b = self.env["account.move"].with_user(self.user_b).search([])
        self.assertIn(invoice_a, found_b)

    def test_access_invoice_same_commercial_partner(self):
        # Contacts of the same company only see their own invoices, unlike the
        # core rule, which grants access to the whole commercial partner
        company = self.env["res.partner"].create(
            {"name": "Company", "is_company": True}
        )
        (self.partner_a | self.partner_b).parent_id = company
        invoice_company = self._create_portal_invoice(company)
        invoice_a = self._create_portal_invoice(self.partner_a)
        invoice_b = self._create_portal_invoice(self.partner_b)
        found_a = self.env["account.move"].with_user(self.user_a).search([])
        self.assertIn(invoice_a, found_a)
        self.assertNotIn(invoice_b, found_a)
        self.assertNotIn(invoice_company, found_a)

    def test_access_invoice_child_contact(self):
        invoice_address = self.env["res.partner"].create(
            {
                "name": "Invoice address A",
                "type": "invoice",
                "parent_id": self.partner_a.id,
            }
        )
        invoice = self._create_portal_invoice(invoice_address)
        found_a = self.env["account.move"].with_user(self.user_a).search([])
        self.assertIn(invoice, found_a)
        found_b = self.env["account.move"].with_user(self.user_b).search([])
        self.assertNotIn(invoice, found_b)

    def test_access_invoice_draft(self):
        invoice_a = self._create_portal_invoice(self.partner_a, post=False)
        found_a = self.env["account.move"].with_user(self.user_a).search([])
        self.assertNotIn(invoice_a, found_a)
        invoice_a.action_post()
        found_a = self.env["account.move"].with_user(self.user_a).search([])
        self.assertIn(invoice_a, found_a)

    def test_access_invoice_line(self):
        invoice_a = self._create_portal_invoice(self.partner_a)
        invoice_b = self._create_portal_invoice(self.partner_b)
        lines_a = self.env["account.move.line"].with_user(self.user_a).search([])
        self.assertTrue(invoice_a.line_ids <= lines_a)
        self.assertFalse(invoice_b.line_ids & lines_a)
        invoice_b.message_subscribe(partner_ids=self.partner_a.ids)
        lines_a = self.env["account.move.line"].with_user(self.user_a).search([])
        self.assertTrue(invoice_b.line_ids <= lines_a)
