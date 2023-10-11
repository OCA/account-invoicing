# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestAccountInvoice(TransactionCase):
    """
    Tests for account.move
    """

    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        self.AccountMove = self.env["account.move"]
        self.AccountAccount = self.env["account.account"]
        self.Product = self.env["product.product"]
        self.supplier = self.env.ref("base.res_partner_3")
        self._prepare_tests()

    def _prepare_tests(self):
        """
        Prepare data for the next tests
        :return: bool
        """
        Product = self.Product
        AccountMove = self.AccountMove
        AccountAccount = self.AccountAccount
        AccountTax = self.env["account.tax"]
        supplier = self.supplier
        account_receivable = AccountAccount.create(
            {
                "code": "200000bis",
                "name": "Sale unit test",
                "account_type": "income",
                "reconcile": True,
            }
        )
        account_payable = AccountAccount.create(
            {
                "code": "220000bis",
                "name": "Expenses unit test",
                "account_type": "expense",
                "reconcile": True,
            }
        )
        tax_p1 = AccountTax.create(
            {
                "name": "percent_tax",
                "amount_type": "percent",
                "amount": 25.0,
                "type_tax_use": "purchase",
            }
        )
        tax_p2 = AccountTax.create(
            {
                "name": "percent_tax",
                "amount_type": "percent",
                "amount": 25.0,
                "type_tax_use": "purchase",
            }
        )
        self.product1 = Product.create(
            {
                "name": "Product purchase type - Unit test 1",
                "purchase_type": True,
                "list_price": 500,
                "property_account_expense_id": account_payable.id,
                "supplier_taxes_id": [Command.set(tax_p1.ids)],
            }
        )
        self.product2 = Product.create(
            {
                "name": "Product purchase type - Unit test 2",
                "purchase_type": True,
                "list_price": 200,
                "property_account_expense_id": account_payable.id,
                "supplier_taxes_id": [Command.set(tax_p2.ids)],
            }
        )
        self.product3 = Product.create(
            {
                "name": "Product purchase type - Unit test 3",
                "purchase_type": True,
                "list_price": 736.25,
                "property_account_expense_id": account_payable.id,
                "supplier_taxes_id": [Command.set(tax_p1.ids)],
            }
        )
        # Check if the supplier is really a supplier
        supplier_invoice_values = {
            "partner_id": supplier.id,
            "move_type": "in_invoice",
            "invoice_line_ids": [
                Command.create(
                    {
                        "name": "Line 1",
                        "account_id": account_receivable.id,
                        "quantity": 2,
                        "price_unit": 100,
                    }
                ),
            ],
        }
        supplier_refund_values = {
            "move_type": "in_refund",
            "partner_id": supplier.id,
            "invoice_line_ids": [
                Command.create(
                    {
                        "name": "Line 1",
                        "account_id": account_receivable.id,
                        "quantity": 2,
                        "price_unit": 523.36,
                    }
                ),
            ],
        }
        customer_invoice_values = {
            "partner_id": supplier.id,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                Command.create(
                    {
                        "name": "Line 1",
                        "account_id": account_receivable.id,
                        "quantity": 2,
                        "price_unit": 523.36,
                    }
                ),
            ],
        }
        self.supplier_invoice = AccountMove.create(supplier_invoice_values)
        self.supplier_refund = AccountMove.create(supplier_refund_values)
        self.customer_invoice = AccountMove.create(customer_invoice_values)

    def test_update_move_line_with_product_type_in_invoice(self):
        # Test update of an account.move with a move_type equals to in_invoice
        lines = self.supplier_invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        )
        for line in lines:
            line.write({"name": "Super Label"})
            self.assertNotEquals(line.tax_ids, self.product1.taxes_id)
            self.assertNotEquals(
                line.account_id, self.product1.property_account_expense_id
            )
            self.assertEqual(line.price_unit, 100)
            self.assertEqual(line.price_subtotal, 200)
            self.assertEqual(line.price_total, 230.0)
        self.assertEqual(self.supplier_invoice.amount_total, 230.0)
        self.assertEqual(self.supplier_invoice.amount_tax, 30.0)

        self.supplier_invoice.write({"product_type_id": self.product1.id})
        lines = self.supplier_invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        )
        for line in lines:
            self.assertEqual(line.product_id, self.product1)
            self.assertEqual(line.name, "Super Label")
            self.assertEqual(line.tax_ids, self.product1.supplier_taxes_id)
            self.assertEqual(line.account_id, self.product1.property_account_expense_id)
            self.assertEqual(line.price_unit, 100.0)
            self.assertEqual(line.price_subtotal, 200.0)
            self.assertEqual(line.price_total, 250.0)
        self.assertEqual(self.supplier_invoice.amount_total, 250.0)
        self.assertEqual(self.supplier_invoice.amount_tax, 50.0)

    def test_update_move_line_with_product_type_in_refund(self):
        # Test update of an account.move with a move_type equals to in_refund
        lines = self.supplier_refund.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        )
        for line in lines:
            line.write({"name": "Super Label"})
            self.assertNotEquals(line.tax_ids, self.product2.taxes_id)
            self.assertNotEquals(
                line.account_id, self.product2.property_account_expense_id
            )
            self.assertEqual(line.price_unit, 523.36)
            self.assertEqual(line.price_subtotal, 1046.72)
            self.assertEqual(line.price_total, 1203.73)
        self.assertEqual(self.supplier_refund.amount_total, 1203.73)
        self.assertEqual(self.supplier_refund.amount_tax, 157.01)

        self.supplier_refund.write({"product_type_id": self.product2.id})
        lines = self.supplier_refund.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        )
        for line in lines:
            self.assertEqual(line.product_id, self.product2)
            self.assertEqual(line.name, "Super Label")
            self.assertEqual(line.tax_ids, self.product2.supplier_taxes_id)
            self.assertEqual(line.account_id, self.product2.property_account_expense_id)
            self.assertEqual(line.price_unit, 523.36)
            self.assertEqual(line.price_subtotal, 1046.72)
            self.assertEqual(line.price_total, 1308.4)
        self.assertEqual(self.supplier_refund.amount_total, 1308.4)
        self.assertEqual(self.supplier_refund.amount_tax, 261.68)

    def test_update_move_line_with_product_type_other_type(self):
        # Test update of an account.move that is not supposed to be updated with a product_type
        lines = self.customer_invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        )
        for line in lines:
            line.write({"name": "Super Label"})
            self.assertNotEquals(line.tax_ids, self.product2.supplier_taxes_id)
            self.assertNotEquals(
                line.account_id, self.product2.property_account_expense_id
            )
            self.assertEqual(line.price_unit, 523.36)
            self.assertEqual(line.price_subtotal, 1046.72)
            self.assertEqual(line.price_total, 1203.73)
        self.assertEqual(self.customer_invoice.amount_total, 1203.73)
        self.assertEqual(self.customer_invoice.amount_tax, 157.01)

        self.customer_invoice.write({"product_type_id": self.product2.id})
        lines = self.customer_invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        )
        for line in lines:
            self.assertFalse(line.product_id)
            self.assertEqual(line.name, "Super Label")
            self.assertNotEquals(line.tax_ids, self.product2.supplier_taxes_id)
            self.assertNotEquals(
                line.account_id, self.product2.property_account_expense_id
            )
            self.assertEqual(line.price_unit, 523.36)
            self.assertEqual(line.price_subtotal, 1046.72)
            self.assertEqual(line.price_total, 1203.73)
        self.assertEqual(self.customer_invoice.amount_total, 1203.73)
        self.assertEqual(self.customer_invoice.amount_tax, 157.01)
