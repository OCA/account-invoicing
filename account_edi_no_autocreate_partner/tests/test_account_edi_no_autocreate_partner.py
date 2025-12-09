# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountEdiNoAutocreatePartner(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super(TestAccountEdiNoAutocreatePartner, cls).setUpClass()
        cls.partner_not_found = cls.env.ref(
            "account_edi_no_autocreate_partner.partner_not_found"
        )

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

    def test_1(self):
        """check partner is not created if not existing"""

        self.assertFalse(self._is_partner_exists())
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        self.assertFalse(self._is_partner_exists())
        self.assertEqual(bill.partner_id, self.partner_not_found)
        return bill

    def test_2(self):
        """check partner_not_found can't be activated"""
        with self.assertRaisesRegex(
            UserError, "You cannot activate the fallback 'Partner Not Found'"
        ):
            self.partner_not_found.active = True

    def test_3(self):
        """check partner_not_found can't be deleted"""
        with self.assertRaisesRegex(
            UserError, "You cannot delete the fallback 'Partner Not Found'"
        ):
            self.partner_not_found.unlink()

    def test_4(self):
        """check invoices linked to partner_not_found can't be posted"""
        bill = self.test_1()
        with self.assertRaisesRegex(
            UserError, "You must assign a proper vendor before posting this invoice"
        ):
            bill.action_post()
        bill.partner_id = self.partner_a
        bill.action_post()
        self.assertEqual(bill.state, "posted")
