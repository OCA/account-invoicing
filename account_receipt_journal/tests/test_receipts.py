from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestReceipts(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.out_receipt_journal = cls.env["account.journal"].create(
            {
                "name": "Sale Receipts Journal",
                "code": "SREC",
                "type": "sale",
                "receipts": True,
                "sequence": 99,
            }
        )
        cls.in_receipt_journal = cls.env["account.journal"].create(
            {
                "name": "Purchase Receipts Journal",
                "code": "PREC",
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

    def test_action_open_dashboard(self):
        """Test action_create_new and open_action"""
        action = self.out_receipt_journal.action_create_new()
        self.assertEqual(action["context"]["default_move_type"], "out_receipt")
        action = self.in_receipt_journal.action_create_new()
        self.assertEqual(action["context"]["default_move_type"], "in_receipt")
        action = self.out_receipt_journal.open_action()
        self.assertEqual(action["context"]["default_move_type"], "out_receipt")
        self.assertEqual(action["domain"], [("move_type", "=", "out_receipt")])
        action = self.in_receipt_journal.open_action()
        self.assertEqual(action["context"]["default_move_type"], "in_receipt")
        self.assertEqual(action["domain"], [("move_type", "=", "in_receipt")])
