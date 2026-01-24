# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.base.tests.common import BaseCommon


class TestResPartnerInvoiceSubject(BaseCommon):
    """
    Test that the onchange on invoice_email_subject
    correctly warns about invalid placeholders.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )

    def test_invalid_placeholders_warning(self):
        self.partner.invoice_email_subject = "Invoice {invoice_number}, {foo}, {bar}"
        onchange_result = self.partner._onchange_invoice_email_subject()
        self.assertIsNotNone(
            onchange_result, "Expected a warning for invalid placeholders"
        )
        self.assertIn(
            "warning", onchange_result, "Warning key missing in onchange result"
        )
        warning = onchange_result["warning"]
        self.assertEqual(warning["title"], "Invalid placeholders")
        self.assertIn("{foo}", warning["message"])
        self.assertIn("{bar}", warning["message"])
        self.assertIn("{invoice_number}", warning["message"])
        self.assertIn("{partner_name}", warning["message"])
        self.assertIn("{invoice_date}", warning["message"])

    def test_valid_placeholders(self):
        """Ensure onchange does nothing when all placeholders are valid."""
        partner = self.env["res.partner"].create(
            {
                "name": "Valid Partner",
                "email": "valid@example.com",
            }
        )
        partner.invoice_email_subject = (
            "Invoice {invoice_number} for {partner_name} on {invoice_date}"
        )
        result = partner._onchange_invoice_email_subject()
        self.assertIsNone(result, "Onchange should do nothing for valid placeholders")

    def test_empty_subject(self):
        """Ensure onchange does nothing when invoice_email_subject is empty."""
        partner = self.env["res.partner"].create(
            {
                "name": "Empty Subject",
                "email": "empty@example.com",
            }
        )
        partner.invoice_email_subject = ""
        result = partner._onchange_invoice_email_subject()
        self.assertIsNone(result)
