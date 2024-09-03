# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestSaleOrderWholeDeliveredInvoiceability(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "whole_delivered_invoiceability": True}
        )
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test product One",
                "invoice_policy": "delivery",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test product Two",
                "invoice_policy": "delivery",
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product_1.name,
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 5,
                            "qty_delivered": 2,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product_2.name,
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 5,
                            "qty_delivered": 5,
                        },
                    ),
                ],
            }
        )

    def test_whole_delivered_invoiceability_partner(self):
        self.assertTrue(self.order.whole_delivered_invoiceability)

    def test_whole_delivered_invoiceability(self):
        self.order.action_confirm()
        self.assertEqual(self.order.invoice_status, "no")
