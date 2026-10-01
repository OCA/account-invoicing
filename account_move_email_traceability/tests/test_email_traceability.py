# Copyright 2026 (APSL - Nagarro) Sara Zambrano
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.mail.tests.common import MailCommon

MAIL_TEMPLATE = """MIME-Version: 1.0
Date: {date}
Message-Id: {msg_id}
Subject: {subject}
From: {email_from}
To: {to}
Content-Type: text/plain

Test email body, without attachment.
"""


@tagged("post_install", "-at_install")
class TestAccountMoveEmailTraceability(MailCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )
        cls.alias_domain = cls.env["mail.alias.domain"].search([], limit=1)
        if not cls.journal.alias_id:
            cls.journal.write(
                {
                    "alias_name": "test-vendor-bills",
                }
            )
        cls.known_partner = cls.env["res.partner"].create(
            {
                "name": "Known Vendor",
                "email": "invoices@knownvendor.com",
                "supplier_rank": 1,
            }
        )

    def test_email_without_attachment_creates_flagged_move(self):
        """An email without attachment must not be lost: the move is
        created flagged as 'email_attachment_missing' and without a
        contact (unknown domain)."""
        self.format_and_process(
            MAIL_TEMPLATE,
            "someone@unknown-domain.com",
            self.journal.alias_id.display_name,
            subject="Inquiry without attached invoice",
            target_model="account.move",
        )

        move = self.env["account.move"].search(
            [("journal_id", "=", self.journal.id)], order="id desc", limit=1
        )

        self.assertTrue(move, "An account.move should have been created anyway")
        self.assertTrue(move.email_attachment_missing)
        self.assertEqual(
            move.email_from_raw and "someone@unknown-domain.com" in move.email_from_raw,
            True,
        )
        self.assertFalse(move.partner_id)
        self.assertTrue(
            move.activity_ids, "A review activity should have been scheduled"
        )

    def test_email_without_attachment_identifies_known_partner(self):
        """If the sender matches an already loaded contact, it is
        auto-filled."""
        self.format_and_process(
            MAIL_TEMPLATE,
            self.known_partner.email,
            self.journal.alias_id.display_name,
            subject="Inquiry without attached invoice",
            target_model="account.move",
        )

        move = self.env["account.move"].search(
            [("journal_id", "=", self.journal.id)], order="id desc", limit=1
        )

        self.assertTrue(move.email_attachment_missing)
        self.assertEqual(move.partner_id, self.known_partner)

    def test_mark_and_undo_email_issue_resolved(self):
        """The 'Mark as resolved' / 'Undo' buttons toggle the traceability
        fields and close/reopen the review activity."""
        self.format_and_process(
            MAIL_TEMPLATE,
            "someone@unknown-domain.com",
            self.journal.alias_id.display_name,
            subject="Inquiry without attached invoice",
            target_model="account.move",
        )
        move = self.env["account.move"].search(
            [("journal_id", "=", self.journal.id)], order="id desc", limit=1
        )
        self.assertTrue(move.activity_ids)

        move.action_mark_email_issue_resolved()
        self.assertEqual(move.email_status, "resolved")
        self.assertTrue(move.email_issue_resolved)
        self.assertFalse(move.email_attachment_missing)

        move.action_undo_email_issue_resolved()
        self.assertEqual(move.email_status, "missing_attachment")

    def test_cron_check_ocr_failures_noop_without_extract_state(self):
        """When no digitization module is installed (no ``extract_state``
        field on account.move), the cron must be a safe no-op."""
        if "extract_state" in self.env["account.move"]._fields:
            self.skipTest(
                "This environment has a digitization module installed "
                "(extract_state field present); the no-op path cannot be "
                "exercised here."
            )
        result = self.env["account.move"]._cron_check_ocr_failures()
        self.assertFalse(result)

    def test_ocr_failure_notify_schedules_activity(self):
        """`_ocr_failure_notify` must create a review activity with the
        expected summary and reference the failure reason in the note."""
        move = self.env["account.move"].search(
            [("journal_id", "=", self.journal.id)], limit=1
        )
        if not move:
            move = self.env["account.move"].create(
                {"journal_id": self.journal.id, "move_type": "in_invoice"}
            )
        move.ocr_failure_reason = "Not enough credit"

        move._ocr_failure_notify()

        activity = move.activity_ids.filtered(
            lambda a: a.summary == "Review invoice with failed digitization"
        )
        self.assertTrue(activity, "The OCR-failure review activity was not created")
        self.assertIn("Not enough credit", activity.note)
        self.assertEqual(
            activity.user_id,
            self.journal.activity_user_id or self.env.user,
        )

    def test_cron_check_ocr_failures_flags_moves(self):
        """When `extract_state` exists and a move is in a failed OCR
        state, the cron must flag it, fill the reason and notify."""
        move = self.env["account.move"].create(
            {"journal_id": self.journal.id, "move_type": "in_invoice"}
        )
        move.ocr_failed = False

        fake_field = type("FakeField", (), {"selection": [("error_status", "Error")]})()
        fake_fields = dict(type(move)._fields)
        fake_fields["extract_state"] = fake_field

        with (
            patch.object(type(move), "_fields", new=fake_fields),
            patch.object(type(move), "extract_state", "error_status", create=True),
            patch.object(type(move), "search", return_value=move),
        ):
            result = self.env["account.move"]._cron_check_ocr_failures()

        self.assertIn(move, result)
        self.assertTrue(move.ocr_failed)
        self.assertEqual(move.ocr_failure_reason, "Error")
        self.assertTrue(
            move.activity_ids.filtered(
                lambda a: a.summary == "Review invoice with failed digitization"
            )
        )
