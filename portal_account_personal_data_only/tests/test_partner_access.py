# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests.common import tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestPartnerAccess(TestAccountReconciliationCommon):
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

    def _create_user(self, letter):
        return self.env["res.users"].create(
            {
                "name": "User %s" % letter,
                "login": "user_%s" % letter,
                "groups_id": [(6, 0, [self.group_portal.id])],
            }
        )

    def _create_partner(self, user):
        return self.env["res.partner"].create(
            {
                "name": user.name,
                "user_ids": [(6, 0, [user.id])],
            }
        )

    def test_access_invoice(self):
        invoice_a = self.create_invoice_partner(partner_id=self.partner_a.id)
        invoice_b = self.create_invoice_partner(partner_id=self.partner_b.id)
        invoice_c = self.create_invoice_partner(partner_id=self.partner_c.id)
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
        invoice_a = self.create_invoice_partner(partner_id=self.partner_a.id)
        invoice_a.message_subscribe(partner_ids=self.partner_b.ids)
        invoices_b = self.env["account.move"].with_user(self.user_b).search([])
        self.assertTrue(invoice_a in invoices_b)
