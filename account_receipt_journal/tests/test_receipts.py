from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestReceipts(AccountTestInvoicingCommon):
    def setUp(self):
        super().setUp()
        self.out_receipt_journal = self.env["account.journal"].create(
            {
                "name": "Sale Receipts Journal",
                "code": "S-REC",
                "type": "sale",
                "receipts": True,
                "sequence": 99,
            }
        )
        self.in_receipt_journal = self.env["account.journal"].create(
            {
                "name": "Purchase Receipts Journal",
                "code": "P-REC",
                "type": "purchase",
                "receipts": True,
                "sequence": 99,
            }
        )

    def test_receipt_journal_sequence(self):
        with self.assertRaises(ValidationError):
            self.out_receipt_journal.write({"sequence": 1})
        with self.assertRaises(ValidationError):
            self.in_receipt_journal.write({"sequence": 1})

    def test_receipt_default_journal(self):
        """Test default values for receipt."""
        for move_type in {"out_receipt", "in_receipt"}:
            with self.subTest(move_type=move_type):
                receipt = self.init_invoice(
                    move_type, products=self.product_a + self.product_b
                )
                self.assertTrue(receipt.journal_id.receipts)

    def test_receipt_exclusive_journal(self):
        """Test exclusivity constraint for receipt journals."""
        for move_type in {"out_receipt", "in_receipt"}:
            with self.subTest(move_type=move_type):
                receipt = self.init_invoice(
                    move_type, products=self.product_a + self.product_b
                )
                non_receipt_journals = self.env["account.journal"].search(
                    [
                        ("type", "=", receipt.journal_id.type),
                        ("company_id", "=", receipt.journal_id.company_id.id),
                        ("receipts", "=", False),
                    ]
                )
                with self.assertRaises(ValidationError):
                    receipt.write({"journal_id": non_receipt_journals.ids[0]})
