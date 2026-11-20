# Copyright 2026 Swanand Beedkar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestAccountInvoicePartnerEmailRecipients(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
            )
        )
        cls.company = cls.env.company

        # Create partners
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Acme Corp Customer",
                "email": "customer@acme.example.com",
            }
        )
        cls.recipient_1 = cls.env["res.partner"].create(
            {
                "name": "Accounting Department",
                "email": "ap@acme.example.com",
                "parent_id": cls.customer.id,
            }
        )
        cls.recipient_2 = cls.env["res.partner"].create(
            {
                "name": "Purchasing Manager",
                "email": "procurement@acme.example.com",
                "parent_id": cls.customer.id,
            }
        )
        cls.recipient_no_email = cls.env["res.partner"].create(
            {
                "name": "No Email Contact",
                "email": False,
                "parent_id": cls.customer.id,
            }
        )

        # Configure recipient_1 and recipient_2 on customer
        cls.customer.invoice_recipient_ids = [
            Command.set([cls.recipient_1.id, cls.recipient_2.id])
        ]

        # Mail template for invoice sending
        cls.mail_template = cls.env.ref(
            "account.email_template_edi_invoice", raise_if_not_found=False
        )
        if not cls.mail_template:
            cls.mail_template = cls.env["mail.template"].create(
                {
                    "name": "Test Invoice Template",
                    "model_id": cls.env["ir.model"]._get_id("account.move"),
                    "use_default_to": True,
                }
            )

        # Base customer invoice
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.customer.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Consulting Service",
                            "price_unit": 1000.0,
                            "quantity": 1.0,
                        }
                    )
                ],
            }
        )

    def test_01_partner_recipients_defaulting_on_invoice(self):
        """AC-1 & AC-2: New invoice inherits invoice_recipient_ids."""
        self.assertEqual(
            self.invoice.invoice_recipient_ids,
            self.recipient_1 | self.recipient_2,
            "Invoice should inherit configured invoice_recipient_ids from partner.",
        )

    def test_02_invoice_recipients_override_on_move(self):
        """AC-2: Overriding invoice_recipient_ids persists independently."""
        new_recipient = self.env["res.partner"].create(
            {"name": "External Auditor", "email": "auditor@audit.example.com"}
        )
        self.invoice.invoice_recipient_ids = [Command.set([new_recipient.id])]
        self.assertEqual(
            self.invoice.invoice_recipient_ids,
            new_recipient,
            "Invoice recipients should be updated to overridden list.",
        )
        self.assertEqual(
            self.customer.invoice_recipient_ids,
            self.recipient_1 | self.recipient_2,
            "Customer partner recipients should remain unchanged on invoice override.",
        )

    def test_03_invoice_recipients_cleared_on_move_respected(self):
        """AC-2: Clearing invoice recipients on draft invoice does not fall back."""
        self.invoice.invoice_recipient_ids = [Command.clear()]
        self.assertFalse(
            self.invoice.invoice_recipient_ids,
            "Invoice recipients should be empty after clearing.",
        )
        self.invoice.action_post()
        # Verify wizard does not re-add partner's recipients
        wizard = (
            self.env["account.move.send.wizard"]
            .with_context(active_model="account.move", active_ids=self.invoice.ids)
            .create({"move_id": self.invoice.id})
        )
        self.assertNotIn(
            self.recipient_1,
            wizard.mail_partner_ids,
            "Clearing recipients must not fall back to partner in wizard.",
        )
        # Verify default send settings do not re-add partner's recipients
        send_model = self.env["account.move.send"]
        default_partners = send_model._get_default_mail_partner_ids(
            self.invoice, self.mail_template, "en_US"
        )
        self.assertNotIn(
            self.recipient_1,
            default_partners,
            "Clearing recipients must not fall back to partner in batch send.",
        )

    def test_04_single_invoice_send_wizard_prepopulation(self):
        """AC-3: Send wizard pre-fills mail_partner_ids with recipients."""
        self.invoice.invoice_recipient_ids = [
            Command.set([self.recipient_1.id, self.recipient_2.id])
        ]
        self.invoice.action_post()
        wizard = (
            self.env["account.move.send.wizard"]
            .with_context(active_model="account.move", active_ids=self.invoice.ids)
            .create({"move_id": self.invoice.id})
        )
        expected_partners = self.customer | self.recipient_1 | self.recipient_2
        self.assertTrue(
            expected_partners <= wizard.mail_partner_ids,
            "Send wizard mail_partner_ids should contain customer and recipients.",
        )

    def test_05_batch_invoice_send_multiple_recipients(self):
        """AC-4: Batch send returns customer and all recipients."""
        self.invoice.invoice_recipient_ids = [
            Command.set([self.recipient_1.id, self.recipient_2.id])
        ]
        self.invoice.action_post()
        send_model = self.env["account.move.send"]
        default_partners = send_model._get_default_mail_partner_ids(
            self.invoice, self.mail_template, "en_US"
        )
        expected_partners = self.customer | self.recipient_1 | self.recipient_2
        self.assertTrue(
            expected_partners <= default_partners,
            "Batch mail partners must include customer and all invoice recipients.",
        )

    def test_06_contact_without_email_handling(self):
        """AC-7: Contact without email address is omitted from mail partner ids."""
        self.invoice.invoice_recipient_ids = [
            Command.set([self.recipient_1.id, self.recipient_no_email.id])
        ]
        send_model = self.env["account.move.send"]
        default_partners = send_model._get_default_mail_partner_ids(
            self.invoice, self.mail_template, "en_US"
        )
        self.assertIn(
            self.recipient_1,
            default_partners,
            "Recipient with valid email must be included.",
        )
        self.assertNotIn(
            self.recipient_no_email,
            default_partners,
            "Recipient without email must be excluded.",
        )

    def test_07_recipient_deduplication(self):
        """AC-6: Duplicate inclusion results in deduplicated recordset."""
        self.invoice.invoice_recipient_ids = [
            Command.set([self.customer.id, self.recipient_1.id])
        ]
        send_model = self.env["account.move.send"]
        default_partners = send_model._get_default_mail_partner_ids(
            self.invoice, self.mail_template, "en_US"
        )
        self.assertEqual(
            len(default_partners),
            len(default_partners.ids),
            "Default partners recordset should have unique IDs without duplication.",
        )

    def test_08_vendor_bill_exclusion(self):
        """Vendor bills (in_invoice) do not compute customer recipients."""
        vendor_bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.customer.id,
            }
        )
        self.assertFalse(
            vendor_bill.invoice_recipient_ids,
            "Vendor bill should not populate customer invoice recipients.",
        )
