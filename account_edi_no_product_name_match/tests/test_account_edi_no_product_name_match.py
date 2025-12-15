# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountEdiNoProductNameMatch(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.product_a.name = "Locations et leasing opérationnel - Véhicule HG6542"

    def _import_invoice(self, journal):
        file_path = "account_edi_ubl_cii/tests/test_files/bis3_bill_example.xml"
        with file_open(file_path, "rb") as file:
            xml_attachment = self.env["ir.attachment"].create(
                {
                    "mimetype": "application/xml",
                    "name": "test_invoice.xml",
                    "raw": file.read(),
                }
            )
        move = (
            self.env["account.journal"]
            .with_context(default_journal_id=journal.id)
            ._create_document_from_attachment(xml_attachment.id)
        )
        return move

    def test_0(self):
        """no matching for the product"""
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertFalse(inv_line.product_id)

    def test_1(self):
        """matching for the product name is enabled"""
        self.env["ir.config_parameter"].sudo().set_param(
            "account_edi.product_name_match", True
        )
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(inv_line.product_id, self.product_a)
