# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestAccountInvoiceTaxRequired(TransactionCase):
    def setUp(self):
        super(TestAccountInvoiceTaxRequired, self).setUp()

        self.account_invoice = self.env["account.move"]
        self.account_journal = self.env["account.journal"]
        self.journal = self.account_journal.create(
            {"code": "test", "name": "test", "type": "sale"}
        )
        self.partner = self.env.ref("base.res_partner_3")
        account_user_type = self.env.ref("account.data_account_type_receivable")

        self.account_account = self.env["account.account"]
        self.account_rec1_id = self.account_account.create(
            dict(
                code="cust_acc",
                name="customer account",
                user_type_id=account_user_type.id,
                reconcile=True,
            )
        )
        self.product_product = self.env["product.product"]
        self.product = self.product_product.create(
            {
                "name": "Test",
                "categ_id": self.env.ref("product.product_category_all").id,
                "standard_price": 50,
                "list_price": 100,
                "type": "service",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "description": "Test",
            }
        )

        invoice_line_data_without_tax = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "quantity": 10.0,
                    "account_id": self.account_account.search(
                        [
                            (
                                "user_type_id",
                                "=",
                                self.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    ).id,
                    "name": "product test 5",
                    "price_unit": 100.00,
                    "currency_id": self.env.ref("base.EUR").id,
                },
            )
        ]
        tax = self.env["account.tax"].create(
            {"name": "Tax 10.0%", "amount": 10.0, "amount_type": "percent"}
        )
        invoice_line_data_with_tax = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "quantity": 10.0,
                    "account_id": self.account_account.search(
                        [
                            (
                                "user_type_id",
                                "=",
                                self.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    ).id,
                    "name": "product test 5",
                    "price_unit": 100.00,
                    "currency_id": self.env.ref("base.EUR").id,
                    "tax_ids": [(6, 0, [tax.id])],
                },
            )
        ]

        self.invoice_without_tax = self.account_invoice.create(
            dict(
                name="Test Customer Invoice Without Tax",
                journal_id=self.journal.id,
                partner_id=self.partner.id,
                invoice_line_ids=invoice_line_data_without_tax,
                type="out_invoice",
            )
        )

        self.invoice_with_tax = self.account_invoice.create(
            dict(
                name="Test Customer Invoice With Tax",
                journal_id=self.journal.id,
                partner_id=self.partner.id,
                invoice_line_ids=invoice_line_data_with_tax,
                type="out_invoice",
            )
        )

    def test_post_account_move_without_tax(self):
        """Validate invoice without tax must raise exception
        """
        with self.assertRaises(exceptions.UserError):
            self.invoice_without_tax.with_context(test_tax_required=True).action_post()
        self.assertNotEqual(self.invoice_with_tax.state, "posted")

    def test_post_account_move_with_tax(self):
        """Validate invoice with tax should not raise exception
        """
        self.invoice_with_tax.with_context(test_tax_required=True).action_post()
        self.assertEqual(self.invoice_with_tax.state, "posted")
