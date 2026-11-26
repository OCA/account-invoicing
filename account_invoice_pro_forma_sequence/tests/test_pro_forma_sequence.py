# Copyright 2021 Lorenzo Battistini @ TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestProFormaSequence(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal_sale = cls.company_data["default_journal_sale"]
        cls.invoice = cls.init_invoice("out_invoice", products=cls.product_a)

    def test_journal_creates_proforma_sequence(self):
        """Sale journals get a pro-forma sequence automatically on create."""
        self.assertTrue(self.journal_sale.pro_forma_sequence_id)
        self.assertIn("PRO-FORMA", self.journal_sale.pro_forma_sequence_id.name)

    def test_journal_non_sale_no_proforma_sequence(self):
        """Non-sale journals should not get a pro-forma sequence."""
        journal_purchase = self.company_data["default_journal_purchase"]
        self.assertFalse(journal_purchase.pro_forma_sequence_id)

    def test_journal_create_new_sale(self):
        """Creating a new sale journal should auto-assign a pro-forma sequence."""
        journal = self.env["account.journal"].create(
            {
                "name": "Test Sale Journal",
                "type": "sale",
                "code": "TSJ",
                "company_id": self.company_data["company"].id,
            }
        )
        self.assertTrue(journal.pro_forma_sequence_id)
        self.assertEqual(
            journal.pro_forma_sequence_id.company_id,
            self.company_data["company"],
        )

    def test_journal_no_duplicate_sequence(self):
        """Calling _set_pro_forma_sequence_id twice should not create duplicates."""
        seq_before = self.journal_sale.pro_forma_sequence_id
        self.journal_sale._set_pro_forma_sequence_id()
        self.assertEqual(self.journal_sale.pro_forma_sequence_id, seq_before)

    def test_assign_proforma_number(self):
        """Assigning a pro-forma number should set number and date."""
        self.assertFalse(self.invoice.proforma_number)
        self.assertFalse(self.invoice.proforma_date)
        self.invoice.assign_proforma_number()
        self.assertTrue(self.invoice.proforma_number)
        self.assertTrue(self.invoice.proforma_date)

    def test_assign_proforma_number_uses_invoice_date(self):
        """Pro-forma date should use invoice date when available."""
        self.invoice.date = "2024-06-15"
        self.invoice.assign_proforma_number()
        self.assertEqual(str(self.invoice.proforma_date), "2024-06-15")

    def test_assign_proforma_number_increments(self):
        """Each assignment should produce a unique sequential number."""
        invoice2 = self.init_invoice("out_invoice", products=self.product_a)
        self.invoice.assign_proforma_number()
        invoice2.assign_proforma_number()
        self.assertNotEqual(self.invoice.proforma_number, invoice2.proforma_number)

    def test_assign_proforma_number_no_sequence_raises(self):
        """Assigning pro-forma on a journal without sequence should raise."""
        self.journal_sale.pro_forma_sequence_id = False
        with self.assertRaises(UserError):
            self.invoice.assign_proforma_number()

    def test_report_without_proforma_number_raises(self):
        """Printing the pro-forma report without a number should raise."""
        report = self.env["report.account_invoice_pro_forma_sequence.report_proforma"]
        with self.assertRaises(UserError):
            report._get_report_values(self.invoice.ids)

    def test_report_with_proforma_number(self):
        """Printing the pro-forma report with a number should succeed."""
        self.invoice.assign_proforma_number()
        report = self.env["report.account_invoice_pro_forma_sequence.report_proforma"]
        result = report._get_report_values(self.invoice.ids)
        self.assertEqual(result["doc_model"], "account.move")
        self.assertEqual(result["docs"], self.invoice)

    def test_print_proforma(self):
        """Print button should return a report action."""
        self.invoice.assign_proforma_number()
        action = self.invoice.with_context(discard_logo_check=True).print_proforma()
        self.assertEqual(action["type"], "ir.actions.report")
        self.assertEqual(
            action["report_name"],
            "account_invoice_pro_forma_sequence.report_proforma",
        )

    def test_proforma_number_not_copied(self):
        """Pro-forma number and date should not be copied."""
        self.invoice.assign_proforma_number()
        invoice_copy = self.invoice.copy()
        self.assertFalse(invoice_copy.proforma_number)
        self.assertFalse(invoice_copy.proforma_date)
