# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.base.tests.common import BaseCommon


class TestResPartner(BaseCommon):
    """
    Tests for partner-specific PDF filename settings.

    Covers:
    - Validation of placeholders in the invoice_pdf_filename field:
      - Correct placeholders ({invoice_number}, {partner_name}, {invoice_date},
       {default})
      - Invalid placeholders trigger a warning
      - Empty filename field is allowed
    - {partner_name} resolves to the actual invoice partner, not the commercial partner.
      This includes cases where the invoice is assigned to a sub-partner of a commercial
      partner.
    - {default} placeholder correctly includes the core report filename

    Setup:
    - Creates a commercial partner with a custom invoice_pdf_filename
    - Creates a default partner with no custom filename
    - Creates invoices assigned to these partners (including sub-partners) to test
    placeholder resolution
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_custom = cls.env["res.partner"].create(
            {
                "name": "Partner Custom",
                "email": "custom@example.com",
                "invoice_pdf_filename": "Invoice_{invoice_number}_{partner_name}",
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

    def test_invalid_placeholders_warning(self):
        """Check warning is returned if PDF filename contains invalid placeholders."""
        self.partner_custom.invoice_pdf_filename = (
            "Invoice {invoice_number}_{foo}_{bar}"
        )
        onchange_result = self.partner_custom._onchange_invoice_pdf_filename()
        self.assertIsNotNone(
            onchange_result, "Expected warning for invalid placeholders"
        )
        self.assertIn("warning", onchange_result, "Warning key missing")
        warning = onchange_result["warning"]
        self.assertEqual(warning["title"], "Invalid placeholders")
        self.assertIn("{foo}", warning["message"])
        self.assertIn("{bar}", warning["message"])
        self.assertIn("{invoice_number}", warning["message"])
        self.assertIn("{partner_name}", warning["message"])
        self.assertIn("{invoice_date}", warning["message"])

    def test_valid_placeholders(self):
        """No warning if all placeholders are valid."""
        self.partner_custom.invoice_pdf_filename = (
            "Invoice {invoice_number} for {partner_name}"
        )
        result = self.partner_custom._onchange_invoice_pdf_filename()
        self.assertIsNone(result, "No warning expected for valid placeholders")

    def test_empty_filename(self):
        """No warning if the filename field is empty."""
        self.partner_custom.invoice_pdf_filename = ""
        result = self.partner_custom._onchange_invoice_pdf_filename()
        self.assertIsNone(result, "No warning expected for empty field")

    def test_partner_name_placeholder(self):
        """
        Ensure {partner_name} uses the actual
        invoice partner, not the commercial partner.
        """
        self.partner_custom.invoice_pdf_filename = (
            "Invoice_{invoice_number}_{partner_name}"
        )
        sub_partner = self.env["res.partner"].create(
            {
                "name": "Sub Partner",
                "parent_id": self.partner_custom.id,
                "email": "sub@example.com",
            }
        )
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": sub_partner.id,
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
        invoice.action_post()
        filename = invoice._get_invoice_report_filename()
        self.assertIn(
            "Sub Partner",
            filename,
            "Expected the direct partner name, not commercial partner",
        )
        self.assertNotIn("Partner Custom_Invoice", filename)
        self.assertTrue(filename.endswith(".pdf"))

    # pylint: disable=missing-return
    def test_default_placeholder_in_custom_filename(self):
        """
        Check that {default} placeholder is replaced
        by the core report filename.
        """
        self.partner_custom.invoice_pdf_filename = "Document_{default}_Extra"
        filename = self.invoice_custom._get_invoice_report_filename()
        core_filename = (
            super(self.invoice_custom.__class__, self.invoice_custom)
            ._get_invoice_report_filename()
            .rsplit(".", 1)[0]
        )
        self.assertIn(core_filename.replace("/", "_"), filename)
        self.assertIn("Extra", filename)
        self.assertTrue(filename.endswith(".pdf"))
