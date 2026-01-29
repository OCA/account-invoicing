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

    def test_access_invoice(self):
        invoice_a = self.init_invoice(
            "out_invoice", partner=self.partner_a, post=True, products=self.product_a
        )
        invoice_b = self.init_invoice(
            "out_invoice", partner=self.partner_b, post=True, products=self.product_a
        )
        invoice_c = self.init_invoice(
            "out_invoice", partner=self.partner_c, post=True, products=self.product_a
        )
        invoice_a.message_subscribe(partner_ids=self.partner_a.ids)
        invoice_b.message_subscribe(partner_ids=self.partner_b.ids)
        invoice_c.message_subscribe(partner_ids=self.partner_c.ids)
        found_a = self.env["account.move"].with_user(self.user_a).search([])
        self.assertTrue(invoice_a in found_a)
        self.assertTrue(invoice_b not in found_a)
        self.assertTrue(invoice_c not in found_a)
        found_b = self.env["account.move"].with_user(self.user_b).search([])
        self.assertTrue(invoice_a not in found_b)
        self.assertTrue(invoice_b in found_b)
        self.assertTrue(invoice_c not in found_b)
        found_c = self.env["account.move"].with_user(self.user_c).search([])
        self.assertTrue(invoice_a not in found_c)
        self.assertTrue(invoice_b not in found_c)
        self.assertTrue(invoice_c in found_c)

    def test_access_invoice_followers(self):
        invoice_a = self.init_invoice(
            "out_invoice", partner=self.partner_a, post=True, products=self.product_a
        )
        invoice_a.message_subscribe(partner_ids=self.partner_a.ids)
        invoice_a.message_subscribe(partner_ids=self.partner_b.ids)
        invoices_b = self.env["account.move"].with_user(self.user_b).search([])
        self.assertTrue(invoice_a in invoices_b)
