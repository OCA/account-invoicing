# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestResPartner(BaseCommon):
    """
    Tests for partner-specific PDF filename settings.
    Based on Jinja-style rendering:
    {{ object.name }}, {{ object.partner_id.name }}, etc.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_custom = cls.env["res.partner"].create(
            {
                "name": "Partner Custom",
                "email": "custom@example.com",
                "invoice_pdf_filename": (
                    "Invoice_{{ object.name }}_{{ object.partner_id.name }}"
                ),
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

    def test_invalid_placeholders_raise_validation_error(self):
        with self.assertRaises(ValidationError) as cm:
            self.partner_custom.write(
                {"invoice_pdf_filename": "Invoice_{{ object.foo }}_{{ object.bar }}"}
            )
        msg = str(cm.exception)
        self.assertIn("foo", msg)
        self.assertIn("bar", msg)

    def test_valid_placeholders(self):
        self.partner_custom.write(
            {
                "invoice_pdf_filename": (
                    "Invoice {{ object.name }} for {{ object.partner_id.name }}"
                )
            }
        )
        self.assertEqual(
            self.partner_custom.invoice_pdf_filename,
            "Invoice {{ object.name }} for {{ object.partner_id.name }}",
        )

    def test_empty_filename_allowed(self):
        self.partner_custom.write({"invoice_pdf_filename": ""})
        self.assertFalse(self.partner_custom.invoice_pdf_filename)

    def test_partner_name_placeholder(self):
        self.partner_custom.write(
            {
                "invoice_pdf_filename": (
                    "Invoice_{{ object.name }}_{{ object.partner_id.name }}"
                )
            }
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
        self.assertIn("Sub Partner", filename.replace("/", "_"))
        self.assertTrue(filename.endswith(".pdf"))

    def test_default_fallback(self):
        filename = self.invoice_default._get_invoice_report_filename()
        self.assertTrue(filename.endswith(".pdf"))
        self.assertIn(self.invoice_default.name.replace("/", "_"), filename)

    def test_template_rendering_adds_extra_content(self):
        self.partner_custom.write(
            {"invoice_pdf_filename": "Document_{{ object.name }}_Extra"}
        )
        filename = self.invoice_custom._get_invoice_report_filename()
        self.assertIn("Extra", filename)
        self.assertTrue(filename.endswith(".pdf"))

    def test_chain_stops_after_non_relational_field(self):
        with self.assertRaises(ValidationError) as cm:
            self.partner_custom.write(
                {"invoice_pdf_filename": "Invoice {{ object.name.partner_id.name }}"}
            )
        msg = str(cm.exception)
        self.assertIn("{{ object.name.partner_id.name }}", msg)
        self.assertIn("Invalid invoice PDF filename fields", msg)
        self.assertIn("name", msg)

    def test_invalid_deep_chain(self):
        with self.assertRaises(ValidationError):
            self.partner_custom.write(
                {"invoice_pdf_filename": "Invoice {{ object.foo.bar.baz }}"}
            )

    def test_invalid_field_after_valid_relational_field(self):
        with self.assertRaises(ValidationError) as cm:
            self.partner_custom.write(
                {"invoice_pdf_filename": "Invoice {{ object.partner_id.foo }}"}
            )
        msg = str(cm.exception)
        self.assertIn("{{ object.partner_id.foo }}", msg)
        self.assertIn("partner_id", msg)

    def test_partial_valid_chain_then_invalid(self):
        with self.assertRaises(ValidationError):
            self.partner_custom.write(
                {
                    "invoice_pdf_filename": (
                        "Invoice {{ object.partner_id.category_id.foo }}"
                    )
                }
            )

    def test_valid_deep_relational_chain(self):
        """Fully valid relational chain must pass validation."""
        self.partner_custom.write(
            {"invoice_pdf_filename": ("Invoice {{ object.partner_id.parent_id.name }}")}
        )
        self.assertIn(
            "{{ object.partner_id.parent_id.name }}",
            self.partner_custom.invoice_pdf_filename,
        )

    def test_mixed_valid_chain_with_text(self):
        """Multiple valid placeholders in one template."""
        self.partner_custom.write(
            {
                "invoice_pdf_filename": (
                    "Invoice {{ object.partner_id.name }} - {{ object.name }}"
                )
            }
        )
        value = self.partner_custom.invoice_pdf_filename
        self.assertIn("partner_id.name", value)
        self.assertIn("name", value)
