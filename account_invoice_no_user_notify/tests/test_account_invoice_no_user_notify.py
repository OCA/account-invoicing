# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import MagicMock, patch

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestAccountInvoiceNoUserNotify(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Customer", "email": "customer@test.com"}
        )
        cls.internal_user = new_test_user(cls.env, login="test-no-notify-user")
        cls.mt_comment = cls.env.ref("mail.mt_comment")
        cls.mt_note = cls.env.ref("mail.mt_note")

    def _make_invoice(self):
        return self.env["account.move"].create(
            {"move_type": "out_invoice", "partner_id": self.partner.id}
        )

    def _mock_recipients(self):
        return [
            {
                "id": self.internal_user.partner_id.id,
                "type": "user",
                "notif": "inbox",
                "groups": [],
            },
            {
                "id": self.partner.id,
                "type": "customer",
                "notif": "email",
                "groups": [],
            },
        ]

    def test_create_sets_no_notify_context(self):
        """Invoice creation passes mail_auto_subscribe_no_notify=True to super.

        We spy on _message_auto_subscribe_notify (which is called during
        auto-subscription) to verify the context flag is already set when
        our create hands control over to the parent chain.
        """
        captured_contexts = []
        AccountMove = type(self.env["account.move"])
        original_notify = AccountMove._message_auto_subscribe_notify

        def spy_notify(self_inner, partner_ids, template):
            captured_contexts.append(
                bool(self_inner.env.context.get("mail_auto_subscribe_no_notify"))
            )
            return original_notify(self_inner, partner_ids, template)

        env = self.env(context=dict(self.env.context, mail_create_nosubscribe=False))
        with patch.object(AccountMove, "_message_auto_subscribe_notify", spy_notify):
            env["account.move"].create(
                {"move_type": "out_invoice", "partner_id": self.partner.id}
            )

        # Every time _message_auto_subscribe_notify is called the flag must be True.
        for flag in captured_contexts:
            self.assertTrue(
                flag,
                "mail_auto_subscribe_no_notify must be True in context "
                "during create",
            )

    def test_notify_get_recipients_filters_users_on_comment(self):
        """User-type recipients are excluded when the message subtype is mt_comment."""
        invoice = self._make_invoice()
        message = MagicMock()
        message.subtype_id = self.mt_comment

        with patch(
            "odoo.addons.mail.models.mail_thread.MailThread._notify_get_recipients",
            return_value=self._mock_recipients(),
        ):
            result = invoice._notify_get_recipients(message, {})

        recipient_types = [r["type"] for r in result]
        self.assertNotIn("user", recipient_types)
        self.assertIn("customer", recipient_types)

    def test_notify_get_recipients_keeps_users_on_non_comment(self):
        """User-type recipients are kept when the message subtype is not mt_comment."""
        invoice = self._make_invoice()
        message = MagicMock()
        message.subtype_id = self.mt_note

        with patch(
            "odoo.addons.mail.models.mail_thread.MailThread._notify_get_recipients",
            return_value=self._mock_recipients(),
        ):
            result = invoice._notify_get_recipients(message, {})

        recipient_types = [r["type"] for r in result]
        self.assertIn("user", recipient_types)
        self.assertIn("customer", recipient_types)

    def test_notify_get_recipients_empty_list(self):
        """No error and empty result when parent returns no recipients."""
        invoice = self._make_invoice()
        message = MagicMock()
        message.subtype_id = self.mt_comment

        with patch(
            "odoo.addons.mail.models.mail_thread.MailThread._notify_get_recipients",
            return_value=[],
        ):
            result = invoice._notify_get_recipients(message, {})

        self.assertEqual(result, [])

    def test_notify_get_recipients_only_users(self):
        """Result is empty when all recipients are internal users and subtype
        is mt_comment."""
        invoice = self._make_invoice()
        message = MagicMock()
        message.subtype_id = self.mt_comment
        only_users = [r for r in self._mock_recipients() if r["type"] == "user"]

        with patch(
            "odoo.addons.mail.models.mail_thread.MailThread._notify_get_recipients",
            return_value=only_users,
        ):
            result = invoice._notify_get_recipients(message, {})

        self.assertEqual(result, [])
