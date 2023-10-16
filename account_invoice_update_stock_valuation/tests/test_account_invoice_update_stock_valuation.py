# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import Form, SavepointCase


class TestAccountInvoiceUpdateStockValuation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product_6 = cls.env.ref("product.product_product_6")
        cls.product_7 = cls.env.ref("product.product_product_7")

    def test_update_stock_valuation_from_invoice(self):
        products = self.product_6
        purchase = self._create_purchase_order(self.partner, products)
        invoice = self._create_invoice_from_purchase(purchase)
        invoice_line = invoice.invoice_line_ids[0].with_context(
            check_move_validity=False
        )
        invoice_line.price_unit += 10.0
        invoice._recompute_dynamic_lines()
        self.assertEqual(invoice_line.stock_valuation_ok, False)
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        invoice_line._compute_stock_valuation_ok()
        self.assertEqual(invoice_line.stock_valuation_ok, True)
        svl = self.env["stock.valuation.layer"].search(
            [
                ("product_id", "=", invoice_line.product_id.id),
                ("account_move_id", "=", invoice.id),
                ("company_id", "=", invoice_line.company_id.id),
                ("value", "=", invoice_line.price_unit),
            ]
        )
        self.assertTrue(svl)

    def _create_purchase_order(self, partner, products):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = partner
        for product in products:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
        return order_form.save()

    def _create_invoice_from_purchase(self, purchase):
        purchase.button_confirm()
        purchase.picking_ids.move_lines.move_line_ids.qty_done = 1
        purchase.picking_ids._action_done()
        purchase.action_create_invoice()
        return purchase.invoice_ids[0].with_context(check_move_validity=False)
