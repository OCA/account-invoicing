# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super(TestModule, self).setUp()
        self.partner = self.env.ref("base.res_partner_12")
        self.product = self.env.ref("product.consu_delivery_01")
        self.product.invoice_policy = "order"

    def test_main(self):
        # Create Pricelist
        pricelist = self.env["product.pricelist"].create({"name": "Demo Pricelist"})
        # Create Product
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                            "qty_delivered": 5,
                        },
                    ),
                ],
            }
        )
        order.action_confirm()
        invoice = order._create_invoices()
        self.assertEqual(
            invoice.pricelist_id,
            order.pricelist_id,
            "Invoice Pricelist has not been recovered from sale order",
        )
