# Copyright 2021 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestProductSupplierinfoForCustomerInvoice(SavepointCase):
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
                "name": cls.customer_1.id,
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
    def _create_invoice(cls, customer):
        return cls.move_model.create(
            {
                "journal_id": cls.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
                "partner_id": customer.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "quantity": 1.0,
                            "name": cls.product.name,
                            "price_unit": 450.00,
                        },
                    ),
                    (
                        0,
                        0,
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
        line = invoice.invoice_line_ids.filtered(lambda l: l.product_id)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_customer_code, "CUST1234")

    def test_02_invoice_line_no_customer_code(self):
        invoice = self._create_invoice(self.customer_2)
        line = invoice.invoice_line_ids.filtered(lambda l: l.product_id)
        self.assertEqual(len(line), 1)
        self.assertFalse(line.product_customer_code)
        line_no_product = invoice.invoice_line_ids.filtered(lambda l: not l.product_id)
        self.assertEqual(len(line_no_product), 1)
        self.assertFalse(line_no_product.product_customer_code)
