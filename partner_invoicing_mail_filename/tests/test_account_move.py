# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from odoo.addons.base.tests.common import BaseCommon


class TestAccountMove(BaseCommon):
    """
    Tests for PDF filename generation in account.move (invoices).

    Covers:
    - Single invoice with custom partner PDF filename
    - Single invoice with default PDF filename
    - Batch processing of multiple invoices with mixed custom/default filenames
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

    def test_custom_filename_single(self):
        """Single invoice: custom partner filename is used."""
        filename = self.invoice_custom._get_invoice_report_filename()

        expected_number = self.invoice_custom.name.replace("/", "_")
        expected_partner = self.partner_custom.name.replace("/", "_")

        self.assertIn(expected_number, filename)
        self.assertIn(expected_partner, filename)
        self.assertTrue(filename.endswith(".pdf"))

    def test_default_filename_single(self):
        """Single invoice: default filename is used if partner has no custom field."""
        filename = self.invoice_default._get_invoice_report_filename()

        self.assertTrue(filename)
        self.assertTrue(filename.endswith(".pdf"))

    def test_batch_filenames(self):
        """Batch invoices: ensures each invoice gets correct PDF filename."""
        invoices = self.env["account.move"].browse(
            [self.invoice_custom.id, self.invoice_default.id]
        )

        filenames = {inv.id: inv._get_invoice_report_filename() for inv in invoices}

        expected_number = self.invoice_custom.name.replace("/", "_")
        expected_partner = self.partner_custom.name.replace("/", "_")

        self.assertIn(expected_number, filenames[self.invoice_custom.id])
        self.assertIn(expected_partner, filenames[self.invoice_custom.id])

        self.assertTrue(filenames[self.invoice_default.id].endswith(".pdf"))

    def test_super_fallback_filename(self):
        self.partner_custom.write({"invoice_pdf_filename": False})
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_custom.id,
                "invoice_date": "2026-01-23",
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
        invoice.action_post()
        filename = invoice._get_invoice_report_filename()
        self.assertTrue(filename.endswith(".pdf"))
        self.assertIn(invoice.name.replace("/", "_"), filename)
