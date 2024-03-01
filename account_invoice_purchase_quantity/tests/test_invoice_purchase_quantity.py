# Copyright 2019 Camptocamp SA
# Copyright ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests.common import Form, TransactionCase


class TestPurchaseOrderInvoicing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
            }
        )
        cls._create_order()

    @classmethod
    def _create_order(cls):
        with Form(cls.env["purchase.order"]) as order_form:
            order_form.partner_id = cls.partner
            with order_form.order_line.new() as line_form:
                line_form.product_id = cls.product
                line_form.product_qty = 10.0
        cls.order = order_form.save()

    @classmethod
    def _process_picking(cls, picking):

        for line in picking.move_line_ids:
            # Receive only partial qty
            line.qty_done = 5.0
        picking._action_done()

    def test_purchase_order_invoice(self):
        # Confirm the whole purchase order with 10.0 quantity
        # Process partially the picking for 5.0
        self.order.button_confirm()
        picking = self.order.picking_ids
        self._process_picking(picking)
        self.order.action_create_invoice()
        invoice = self.order.invoice_ids
        line_product = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.product
        )
        self.assertTrue(line_product)
        self.assertEqual(line_product.quantity, 5.0)
        self.assertEqual(line_product.purchase_line_qty_received, 5.0)
        self.assertEqual(line_product.purchase_line_product_qty, 10)
