# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import Form, TransactionCase


class TestSaleInvoicingDateSelection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "partner - test"})
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner1 - test"})
        cls.product = cls.env["product.product"].create(
            {"name": "test invoicing", "type": "service", "invoice_policy": "order"}
        )

    def _create_sale_order(self, partner):
        with Form(self.env["sale.order"]) as sale_form:
            sale_form.partner_id = partner
            with sale_form.order_line.new() as so_line_form:
                so_line_form.product_id = self.product
                so_line_form.price_unit = 100.00
        return sale_form.save()

    def test_andvance_invoice(self):
        self.sale_order_1 = self._create_sale_order(self.partner)
        self.sale_order_2 = self._create_sale_order(self.partner_1)
        self.sale_order_1.action_confirm()
        self.sale_order_2.action_confirm()
        orders = self.sale_order_1 + self.sale_order_2
        with Form(
            self.env["sale.advance.payment.inv"].with_context(
                active_model="sale.order", active_ids=orders.ids, open_invoices=True
            )
        ) as wiz_invoice_form:
            wiz_invoice_form.invoice_date = "2022-11-01"
        wiz = wiz_invoice_form.save()
        action = wiz.create_invoices()
        invoices = self.env["account.move"].search(action["domain"])
        self.assertEqual(fields.Date.to_string(invoices[0].invoice_date), "2022-11-01")
        self.assertEqual(fields.Date.to_string(invoices[1].invoice_date), "2022-11-01")
