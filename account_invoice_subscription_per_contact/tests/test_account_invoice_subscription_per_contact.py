# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestAccountInvoiceSubscriptionPerContact(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=False,
                mail_create_nosubscribe=False,
            )
        )
        cls.user = new_test_user(cls.env, login="test-user1")
        cls.customer_1 = cls.env["res.partner"].create({"name": "Test customer 1"})
        cls.customer_1_child = cls.env["res.partner"].create(
            {"name": "Test contact", "parent_id": cls.customer_1.id}
        )
        cls.customer_2 = cls.env["res.partner"].create({"name": "Test customer 2"})

    def test_account_invoice_message_subscribe(self):
        self.customer_1.message_subscribe(
            partner_ids=self.user.partner_id.ids,
            subtype_ids=self.env.ref(
                "account_invoice_subscription_per_contact.mt_invoice_new"
            ).ids,
        )
        invoice_1 = self.env["account.move"].create(
            {"partner_id": self.customer_1.id, "move_type": "out_invoice"}
        )
        self.assertIn(
            self.user.partner_id, invoice_1.message_follower_ids.mapped("partner_id")
        )
        invoice_1_child = self.env["account.move"].create(
            {"partner_id": self.customer_1_child.id, "move_type": "out_invoice"}
        )
        self.assertIn(
            self.user.partner_id,
            invoice_1_child.message_follower_ids.mapped("partner_id"),
        )
        invoice_2 = self.env["account.move"].create(
            {"partner_id": self.customer_2.id, "move_type": "out_invoice"}
        )
        self.assertNotIn(
            self.user.partner_id, invoice_2.message_follower_ids.mapped("partner_id")
        )
