# Copyright 2026 Michael Tietz (MT Software) <mtietz@mt-software.de>
from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("-at_install", "post_install")
class Common(TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpClassOrder()

    @classmethod
    def setUpClassOrder(cls):
        cls.product_a.invoice_policy = "order"
        cls.product_b.invoice_policy = "order"
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Europe pricelist", "currency_id": cls.env.ref("base.EUR").id}
        )
        cls.order1_p1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "client_order_ref": "ref123",
                "pricelist_id": cls.pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "order 1 line 1",
                            "product_id": cls.product_a.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom_id": cls.product_a.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "order 1 line 2",
                            "product_id": cls.product_b.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom_id": cls.product_a.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.order1_p1.action_confirm()
        cls.order2_p1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "order 2 line 1",
                            "product_id": cls.product_a.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom_id": cls.product_a.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "order 2 line 2",
                            "product_id": cls.product_b.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom_id": cls.product_a.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.order2_p1.action_confirm()
