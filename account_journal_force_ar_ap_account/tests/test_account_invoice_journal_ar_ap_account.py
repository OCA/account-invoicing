from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class AccountInvoiceJournalArApAccount(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ResPartner = cls.env["res.partner"]
        AccountJournal = cls.env["account.journal"]
        ProductProduct = cls.env["product.product"]
        AccountAccount = cls.env["account.account"]
        ProductCategory = cls.env["product.category"]
        cls.product_category = ProductCategory.create(
            {
                "name": "Test category",
            }
        )
        cls.journal = AccountJournal.create(
            {"code": "test", "name": "test", "type": "sale"}
        )
        cls.account_1_id = AccountAccount.create(
            {
                "code": "999999991",
                "name": "customer account test",
                "account_type": "asset_receivable",
            }
        )
        cls.partner = ResPartner.create(
            {
                "name": "Test Partner",
                "property_account_receivable_id": cls.account_1_id.id,
            }
        )
        cls.account_2_id = AccountAccount.create(
            {
                "code": "999999992",
                "name": "customer account test",
                "account_type": "asset_receivable",
            }
        )
        cls.product = ProductProduct.create(
            {
                "name": "Test",
                "list_price": 100,
                "type": "consu",
                "categ_id": cls.product_category.id,
            }
        )
        cls.invoice_data = {
            "journal_id": cls.journal.id,
            "partner_id": cls.partner.id,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                Command.create(
                    {
                        "product_id": cls.product.id,
                        "quantity": 1.0,
                        "account_id": AccountAccount.search(
                            [
                                (
                                    "account_type",
                                    "=",
                                    "income",
                                )
                            ],
                            limit=1,
                        ).id,
                        "name": cls.product.name,
                        "price_unit": 10.00,
                    },
                )
            ],
        }

    def test_compute_account_id(self):
        AccountMove = self.env["account.move"]
        invoice = AccountMove.create(self.invoice_data)
        lines = invoice.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        )
        self.assertEqual(set(lines.mapped("account_id")), {self.account_1_id})
        self.assertNotEqual(set(lines.mapped("account_id")), {self.account_2_id})
        self.journal.ar_ap_account_id = self.account_2_id
        invoice2 = AccountMove.create(self.invoice_data)
        lines2 = invoice2.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        )
        self.assertEqual(set(lines2.mapped("account_id")), {self.account_2_id})
        self.assertNotEqual(set(lines2.mapped("account_id")), {self.account_1_id})
        self.assertNotEqual(
            set(lines.mapped("account_id")), set(lines2.mapped("account_id"))
        )
