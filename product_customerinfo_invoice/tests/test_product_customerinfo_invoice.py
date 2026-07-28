# Copyright 2021 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProductCustomerInfoInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_model = cls.env["account.move"]
        cls.customerinfo_model = cls.env["product.customerinfo"]
        cls.pricelist_model = cls.env["product.pricelist"]
        cls.customer_1 = cls._create_customer("customer1")
        cls.customer_2 = cls._create_customer("customer2")

        cls.company = cls.env.ref("base.main_company")
        cls.product = cls.env.ref("product.product_product_4")
        cls.customerinfo_1 = cls.customerinfo_model.create(
            {
                "partner_id": cls.customer_1.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_id": cls.product.id,
                "product_code": "CUST1234",
            }
        )

    @classmethod
    def _create_customer(cls, name):
        return cls.env["res.partner"].create(
            {"name": name, "email": "example@yourcompany.com", "phone": 123456}
        )

    @classmethod
    def _create_invoice(cls, customer, move_type="out_invoice"):
        journal_type = (
            "sale" if move_type in ("out_invoice", "out_refund") else "purchase"
        )
        return cls.move_model.create(
            {
                "journal_id": cls.env["account.journal"]
                .search([("type", "=", journal_type)], limit=1)
                .id,
                "partner_id": customer.id,
                "move_type": move_type,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1.0,
                            "name": cls.product.name,
                            "price_unit": 450.00,
                        },
                    ),
                    Command.create(
                        {
                            "name": "Line without product",
                            "quantity": 1.0,
                            "price_unit": 50.00,
                        },
                    ),
                ],
            }
        )

    def test_01_invoice_line_customer_code(self):
        invoice = self._create_invoice(self.customer_1)
        line = invoice.invoice_line_ids.filtered(lambda il: il.product_id)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_customer_code, "CUST1234")

    def test_02_invoice_line_no_customer_code(self):
        invoice = self._create_invoice(self.customer_2)
        line = invoice.invoice_line_ids.filtered(lambda il: il.product_id)
        self.assertEqual(len(line), 1)
        self.assertFalse(line.product_customer_code)
        line_no_product = invoice.invoice_line_ids.filtered(
            lambda il: not il.product_id
        )
        self.assertEqual(len(line_no_product), 1)
        self.assertFalse(line_no_product.product_customer_code)

    def test_03_partner_show_customer_code(self):
        invoice = self._create_invoice(self.customer_1)
        self.assertTrue(invoice.partner_show_customer_code)
        bill = self._create_invoice(self.customer_1, move_type="in_invoice")
        self.assertFalse(bill.partner_show_customer_code)
        bill_line = bill.invoice_line_ids.filtered(lambda il: il.product_id)
        self.assertEqual(len(bill_line), 1)
        self.assertFalse(bill_line.product_customer_code)
