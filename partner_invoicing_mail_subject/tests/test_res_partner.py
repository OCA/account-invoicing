# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestResPartnerInvoiceSubject(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )

        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test",
                            "quantity": 1,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        cls.invoice.action_post()

    def test_invalid_object_field_raises(self):
        with self.assertRaises(ValidationError):
            self.partner.write(
                {"invoice_email_subject": "Invoice {{ object.non_existing }}"}
            )

    def test_valid_object_field(self):
        self.partner.write({"invoice_email_subject": "Invoice {{ object.name }}"})
        self.assertEqual(
            self.partner.invoice_email_subject, "Invoice {{ object.name }}"
        )

    def test_empty_subject_allowed(self):
        self.partner.write({"invoice_email_subject": ""})
        self.assertFalse(self.partner.invoice_email_subject)

    def test_render_integration(self):
        self.partner.write({"invoice_email_subject": "Invoice {{ object.name }}"})
        subject = self.env["account.move.send"]._get_default_mail_subject(
            self.invoice,
            self.env.ref("account.email_template_edi_invoice"),
            self.partner.lang,
        )
        self.assertIn(self.invoice.name, subject)

    def test_relational_field_validation(self):
        self.partner.write(
            {"invoice_email_subject": "Invoice {{ object.partner_id.name }}"}
        )
        self.assertIn(
            "{{ object.partner_id.name }}", self.partner.invoice_email_subject
        )

    def test_invalid_chain_after_non_relational_field(self):
        with self.assertRaises(ValidationError):
            self.partner.write(
                {"invoice_email_subject": "Invoice {{ object.name.partner_id.name }}"}
            )
