from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestReceipts(AccountTestInvoicingCommon):
    def setUp(self):
        super(TestReceipts, self).setUp()
        self.move_model = self.env["account.move"]
        self.tax_model = self.env["account.tax"]
        self.journal_model = self.env["account.journal"]
        self.a_sale = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )
        self.tax22inc = self.tax_model.create(
            {
                "name": "Tax 22 INC",
                "amount": 22,
                "price_include": True,
            }
        )
        self.receipt_journal = self.create_receipt_journal()

    def create_receipt_journal(self):
        return self.journal_model.create(
            {
                "name": "Sale Receipts Journal",
                "code": "S-REC",
                "type": "sale",
                "receipts": True,
                "sequence": 99,
            }
        )

    def create_receipt(self):
        receipt = self.move_model.with_context(default_move_type="out_receipt").create(
            {
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.a_sale.id,
                            "product_id": self.env.ref("product.product_product_5").id,
                            "name": "Receipt",
                            "quantity": 1,
                            "price_unit": 10,
                            "tax_ids": [(6, 0, {self.tax22inc.id})],
                        },
                    ),
                ]
            }
        )
        return receipt

    def test_receipt_journal_default(self):
        """Test default values for receipt."""
        receipt = self.create_receipt()
        self.assertEqual(receipt.journal_id.id, self.receipt_journal.id)
