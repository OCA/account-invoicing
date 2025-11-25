# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountEdiRetrievePartner(AccountTestInvoicingCommon):
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

    def _is_partner_exists(self):
        return bool(self.env["res.partner"].search([("vat", "=", "LU12977109")]))

    def test_0(self):
        """check partner is created if not existing"""
        self.assertFalse(self._is_partner_exists())
        self._import_invoice(self.company_data["default_journal_purchase"])
        self.assertTrue(self._is_partner_exists())

    def test_1(self):
        """check partner is used if already existing"""
        partner = self.env["res.partner"].create(
            {"vat": "LU12977109", "name": "partner test"}
        )
        self.assertTrue(self._is_partner_exists())
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        self.assertEqual(bill.partner_id, partner)

    def test_2(self):
        """commercial partner is used if child matched"""
        partner = self.env["res.partner"].create({"name": "partner test"})
        self.env["res.partner"].create(
            {
                "email": "adl@test.com",
                "name": "child partner test",
                "parent_id": partner.id,
            }
        )
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        self.assertEqual(bill.partner_id, partner)
