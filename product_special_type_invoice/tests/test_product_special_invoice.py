# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestProductSpecialInvoice(common.TransactionCase):
    def setUp(self):
        super(TestProductSpecialInvoice, self).setUp()
        self.product_obj = self.env["product.product"]
        self.line_obj = self.env["account.invoice.line"]
        self.invoice_obj = self.env["account.invoice"]
        self.agrolait = self.env.ref("base.res_partner_2")
        self.product_3 = self.env.ref("product.product_product_3")
        self.product_2 = self.env.ref("product.product_product_2")
        self.product_1 = self.env.ref("product.product_product_1")
        self.product_1.special_type = "fee"
        vals = {
            "name": "Advance Product",
            "special_type": "advance",
            "type": "service",
        }
        self.advance = self.product_obj.create(vals)

        vals = {
            "name": "Delivery Product",
            "special_type": "delivery",
            "type": "service",
            "list_price": 30.0,
        }
        self.delivery = self.product_obj.create(vals)

        vals = {
            "name": "Discount Product",
            "special_type": "discount",
            "type": "service",
            "list_price": "-15.0",
        }
        self.discount = self.product_obj.create(vals)

    def _create_line(self, product, qty):
        vals = {
            "product_id": product.id,
            "quantity": qty,
            "invoice_id": self.invoice.id,
        }
        line = self.line_obj.new(vals)
        line._onchange_product_id()
        values = line._convert_to_write({name: line[name] for name in line._cache})
        return self.line_obj.create(values)

    def _create_invoice(self):
        vals = {
            "partner_id": self.agrolait.id,
        }
        self.invoice = self.invoice_obj.create(vals)

    def test_product_special_invoice(self):
        self._create_invoice()
        self.line1 = self._create_line(self.product_1, 10.0)
        self.line2 = self._create_line(self.product_2, 5.0)
        self.line3 = self._create_line(self.product_3, 3.0)
        self.line3 = self._create_line(self.discount, 1.0)
        self.line3 = self._create_line(self.delivery, 1.0)
        self.line3 = self._create_line(self.advance, 1.0)
        self.line3 = self._create_line(self.advance, 1.0)

        self.assertEqual(
            307.5,
            self.invoice.fees_amount,
        )
        self.assertEqual(
            30.0,
            self.invoice.delivery_amount,
        )
        self.assertEqual(
            -15.0,
            self.invoice.extra_discount_amount,
        )
        self.assertEqual(
            2.0,
            self.invoice.advance_amount,
        )
        # (38.25 * 5 = 191.25) + (450.0 * 3 = 1350) + 307.5 - 15.0
        # + 30.0 +  2.0
        self.assertEqual(
            1865.75,
            self.invoice.amount_untaxed,
        )
