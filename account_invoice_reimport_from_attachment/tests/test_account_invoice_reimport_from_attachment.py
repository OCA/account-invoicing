# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceReimportFromAttachment(AccountTestInvoicingCommon):
    def _import_invoice(self, journal, file_path=None):
        if file_path is None:
            file_path = (
                "account_invoice_reimport_from_attachment/tests/test_files/"
                "bis3_bill_example.xml"
            )
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

    def _test_import_bill(self):
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        attachment = bill.attachment_ids
        self.assertEqual(len(attachment), 1)
        self.assertEqual(len(bill.invoice_line_ids), 1)
        return bill, attachment

    def _test_give_user_reimport_group(self):
        self.env.user.groups_id += self.env.ref(
            "account_invoice_reimport_from_attachment."
            "group_invoice_reimport_from_attachment"
        )

    def _test_reimport(self, bill, attachment):
        action = bill.action_open_reimport_wizard()
        wizard = (
            self.env[action.get("res_model")]
            .with_context(**action.get("context"))
            .create({"attachment_id": attachment.id})
        )
        self.assertEqual(wizard.available_attachment_ids, attachment)
        wizard.action_confirm()

    def test_1(self):
        bill, attachment = self._test_import_bill()
        bill.invoice_line_ids.unlink()
        self.assertEqual(len(bill.invoice_line_ids), 0)
        with self.assertRaisesRegex(
            AccessError, "You are not allowed to re-import invoices from attachments"
        ):
            bill.action_open_reimport_wizard()
        self._test_give_user_reimport_group()
        self._test_reimport(bill, attachment)
        self.assertEqual(len(bill.invoice_line_ids), 1)
        self.assertEqual(bill.attachment_ids, attachment)

    def test_2(self):
        """reimport on posted invoices is not allowed"""
        bill, attachment = self._test_import_bill()
        bill.action_post()
        self.assertEqual(bill.state, "posted")
        self._test_give_user_reimport_group()
        with self.assertRaisesRegex(
            UserError, "You can only re-import lines on a draft invoice."
        ):
            self._test_reimport(bill, attachment)
