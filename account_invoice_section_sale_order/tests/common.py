from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged("-at_install", "post_install")
class Common(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpClassOrder()

    @classmethod
    def setUpClassOrder(cls):
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_2 = cls.env.ref("product.product_product_2")
        cls.product_1.invoice_policy = "order"
        cls.product_2.invoice_policy = "order"
        cls.order1_p1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "partner_shipping_id": cls.partner_1.id,
                "partner_invoice_id": cls.partner_1.id,
                "client_order_ref": "ref123",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "order 1 line 1",
                            "product_id": cls.product_1.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "order 1 line 2",
                            "product_id": cls.product_2.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.order1_p1.action_confirm()
        cls.order2_p1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "partner_shipping_id": cls.partner_1.id,
                "partner_invoice_id": cls.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "order 2 line 1",
                            "product_id": cls.product_1.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "order 2 line 2",
                            "product_id": cls.product_2.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.order2_p1.action_confirm()
