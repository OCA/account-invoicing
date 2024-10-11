# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        partner = cls.env.ref("base.res_partner_12")
        product = cls.env.ref("product.consu_delivery_01")
        product.invoice_policy = "order"
        pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Demo Pricelist",
                "discount_policy": "without_discount",
                "item_ids": [(0, 0, {"compute_price": "fixed", "fixed_price": 1.0})],
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "product_uom": product.uom_id.id,
                            "price_unit": product.list_price,
                            "qty_delivered": 5,
                        },
                    )
                ],
            }
        )

    def test_sale_order_action_confirm(self):
        self.order.action_confirm()
        invoice = self.order._create_invoices()
        self.assertEqual(
            invoice.pricelist_id,
            self.order.pricelist_id,
            "Invoice Pricelist has not been recovered from sale order",
        )
        self.assertEqual(invoice.amount_total, self.order.amount_total)
        sale_line = self.order.order_line[0]
        inv_line = invoice.line_ids[0]
        self.assertEqual(sale_line.product_uom_qty, inv_line.quantity)
        self.assertEqual(sale_line.price_unit, inv_line.price_unit)
        self.assertEqual(sale_line.discount, inv_line.discount)

    def test_sale_order_refund_action_confirm(self):
        sale_line = self.order.order_line[0]
        sale_line.product_uom_qty = -5
        sale_line.qty_delivered = -5
        self.order.action_confirm()
        invoice = self.order._create_invoices(final=True)
        self.assertEqual(
            invoice.pricelist_id,
            self.order.pricelist_id,
            "Invoice Pricelist has not been recovered from sale order",
        )
        self.assertEqual(-invoice.amount_total, self.order.amount_total)
        inv_line = invoice.line_ids[0]
        self.assertEqual(-sale_line.product_uom_qty, inv_line.quantity)
        self.assertEqual(sale_line.price_unit, inv_line.price_unit)
        self.assertEqual(sale_line.discount, inv_line.discount)
