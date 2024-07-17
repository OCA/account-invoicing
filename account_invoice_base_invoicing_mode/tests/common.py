# Copyright 2021 Camptocamp SA
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import SavepointCase


class TestInvoiceModeCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.SaleOrder = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner2 = cls.env.ref("base.res_partner_2")
        cls.product = cls.env["product.product"].create(
            {"name": "Test", "type": "service"}
        )
        cls.pt1 = cls.env["account.payment.term"].create({"name": "Term Two"})
        cls.pt2 = cls.env["account.payment.term"].create({"name": "Term One"})
        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "payment_term_id": cls.pt1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Line one",
                            "product_id": cls.product.id,
                            "product_uom_qty": 4,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 123,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        # Lets give the saleorder the same partner and payment terms
        cls.so2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "payment_term_id": cls.pt1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Line one",
                            "product_id": cls.product.id,
                            "product_uom_qty": 4,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 123,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.company = cls.so1.company_id

    def deliver_invoice(self, sale_order):
        sale_order.action_confirm()
        for line in sale_order.order_line:
            line.qty_delivered_manual = line.product_uom_qty
