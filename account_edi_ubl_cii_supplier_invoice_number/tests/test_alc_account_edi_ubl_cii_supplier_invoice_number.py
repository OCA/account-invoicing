# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAlcAccountEdiUblCiiSupplierInvoiceNumber(AccountTestInvoicingCommon):
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

    def test_import_vendor_bill(self):
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        self.assertEqual(bill.ref, "FAC/2023/00052")
        self.assertEqual(bill.supplier_invoice_number, "FAC/2023/00052")

    def test_import_customer_invoice(self):
        invoice = self._import_invoice(self.company_data["default_journal_sale"])
        self.assertEqual(invoice.ref, "FAC/2023/00052")
        self.assertFalse(invoice.supplier_invoice_number)
