# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.base.tests.common import BaseCommon


class TestAccountMoveSend(BaseCommon):
    """
    Tests that invoice email subjects are correctly set per partner.

    Covers:
    - Single invoice with custom partner subject
    - Single invoice with default subject
    - Batch sending with mixed custom/default subjects
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_custom = cls.env["res.partner"].create(
            {
                "name": "Partner Custom",
                "email": "custom@example.com",
                "invoice_email_subject": "Custom Invoice Subject",
                "invoice_sending_method": "email",
            }
        )
        cls.partner_default = cls.env["res.partner"].create(
            {
                "name": "Partner Default",
                "email": "default@example.com",
            }
        )
        cls.invoice_custom = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_custom.id,
                "invoice_date": "2026-01-23",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        cls.invoice_custom.action_post()
        cls.invoice_default = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_default.id,
                "invoice_date": "2026-01-23",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product 2",
                            "quantity": 2,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        cls.invoice_default.action_post()

    def test_individual_subject_single(self):
        """
        Single invoice: ensures the partner-specific
        subject is applied.
        """
        wizard = self.env["account.move.send.wizard"].create(
            {
                "move_id": self.invoice_custom.id,
            }
        )
        subject = wizard._get_default_mail_subject(
            self.invoice_custom,
            wizard.template_id,
            wizard.lang,
        )
        self.assertEqual(subject, "Custom Invoice Subject")

    def test_default_subject_single(self):
        """
        Single invoice with no partner-specific subject:
        ensures the standard subject is used.
        """
        wizard = self.env["account.move.send.wizard"].create(
            {
                "move_id": self.invoice_default.id,
            }
        )
        subject = wizard._get_default_mail_subject(
            self.invoice_default,
            wizard.template_id,
            wizard.lang,
        )
        self.assertTrue(subject)
        self.assertIn(self.invoice_default.name, subject)

    def test_batch_subjects(self):
        """
        Batch sending: ensures each invoice gets the
        correct subject (custom or default).
        """
        wizard_batch = self.env["account.move.send.batch.wizard"].create(
            {"move_ids": [(6, 0, [self.invoice_custom.id, self.invoice_default.id])]}
        )
        template = self.env.ref(
            "account.email_template_edi_invoice", raise_if_not_found=False
        )
        subjects = {}
        for move in wizard_batch.move_ids:
            subjects[move.id] = self.env["account.move.send"]._get_default_mail_subject(
                move,
                template,
                move.partner_id.lang,
            )

        self.assertEqual(subjects[self.invoice_custom.id], "Custom Invoice Subject")
        self.assertIsNotNone(subjects[self.invoice_default.id])
        self.assertIn(self.invoice_default.name, subjects[self.invoice_default.id])

    def test_child_partner_subject(self):
        """
        Single invoice for a child contact: ensures the commercial partner's
        invoice_email_subject is used.
        """
        child_partner = self.env["res.partner"].create(
            {
                "name": "Child Partner",
                "parent_id": self.partner_custom.id,
                "email": "child@example.com",
            }
        )
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": child_partner.id,
                "invoice_date": "2026-01-23",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Child Product",
                            "quantity": 1,
                            "price_unit": 123,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        wizard = self.env["account.move.send.wizard"].create({"move_id": invoice.id})
        subject = wizard._get_default_mail_subject(
            invoice, wizard.template_id, invoice.partner_id.lang
        )
        self.assertEqual(subject, "Custom Invoice Subject")

    def test_child_partner_default_subject(self):
        """
        Single invoice for a child contact without a custom subject:
        ensures the standard email template subject is used.
        """
        child_partner = self.env["res.partner"].create(
            {
                "name": "Child No Subject",
                "parent_id": self.partner_default.id,
                "email": "child_no_subject@example.com",
            }
        )
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": child_partner.id,
                "invoice_date": "2026-01-23",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Child Product",
                            "quantity": 1,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        wizard = self.env["account.move.send.wizard"].create({"move_id": invoice.id})
        subject = wizard._get_default_mail_subject(
            invoice, wizard.template_id, invoice.partner_id.lang
        )
        self.assertIsNotNone(subject)
        self.assertIn(invoice.name, subject)

    def test_custom_subject_skipped_for_non_email_method(self):
        """
        Custom subject should NOT be used if invoice_sending_method != 'email'.
        """
        partner = self.env["res.partner"].create(
            {
                "name": "Partner Print",
                "email": "print@example.com",
                "invoice_email_subject": "Should Not Use",
                "invoice_sending_method": "manual",
            }
        )
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_date": "2026-01-23",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Print Product",
                            "quantity": 1,
                            "price_unit": 75,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        wizard = self.env["account.move.send.wizard"].create({"move_id": invoice.id})
        subject = wizard._get_default_mail_subject(
            invoice, wizard.template_id, invoice.partner_id.lang
        )
        self.assertIsNotNone(subject)
        self.assertNotEqual(subject, "Should Not Use")
        self.assertIn(invoice.name, subject)

    def test_custom_subject_with_placeholders(self):
        """
        Ensures that placeholders in the custom subject are correctly replaced.
        """
        self.partner_custom.invoice_email_subject = (
            "Invoice {invoice_number} for {partner_name} on {invoice_date}"
        )
        wizard = self.env["account.move.send.wizard"].create(
            {"move_id": self.invoice_custom.id}
        )
        subject = wizard._get_default_mail_subject(
            self.invoice_custom, wizard.template_id, self.invoice_custom.partner_id.lang
        )
        expected = (
            f"Invoice {self.invoice_custom.name.replace('/', '_')} "
            f"for {self.partner_custom.name.replace('/', '_')} "
            f"on {self.invoice_custom.invoice_date}"
        )
        self.assertEqual(subject, expected)
