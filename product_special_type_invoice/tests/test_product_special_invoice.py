# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, common


class TestProductSpecialInvoice(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.precision = self.env["decimal.precision"].precision_get("Account")
        self.product_obj = self.env["product.product"]
        self.line_obj = self.env["account.move.line"]
        self.invoice_obj = self.env["account.move"]
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
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = product
                line_form.quantity = qty
        return None

    def _create_invoice(self):
        with Form(
            self.invoice_obj.with_context(default_move_type="out_invoice")
        ) as invoice_form:
            invoice_form.partner_id = self.agrolait
            self.invoice = invoice = invoice_form.save()
        return invoice

    def test_product_special_invoice(self):
        self._create_invoice()
        self._create_line(self.product_1, 10.0)
        self._create_line(self.product_2, 5.0)
        self._create_line(self.product_3, 3.0)
        self._create_line(self.discount, 1.0)
        self._create_line(self.delivery, 1.0)
        self._create_line(self.advance, 1.0)
        self._create_line(self.advance, 1.0)

        self.assertAlmostEqual(307.5, self.invoice.fees_amount, self.precision)
        self.assertAlmostEqual(30, self.invoice.delivery_amount, self.precision)
        self.assertAlmostEqual(
            -15.0, self.invoice.extra_discount_amount, self.precision
        )
        self.assertAlmostEqual(2.0, self.invoice.advance_amount, self.precision)
        # (38.25 * 5 = 191.25) + (450.0 * 3 = 1350) + 307.5 - 15.0
        # + 30.0 +  2.0
        self.assertAlmostEqual(1865.75, self.invoice.amount_untaxed, self.precision)
