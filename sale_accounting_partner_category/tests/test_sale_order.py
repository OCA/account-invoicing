# Copyright 2022 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import SavepointCase


class TestSaleOrderAccountingPartnerCategory(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.tag = cls.env["accounting.partner.category"].create({"name": "Tag 1"})
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.partner.accounting_category_ids = cls.tag

        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "service", "invoice_policy": "order"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        cls.order.action_confirm()

    def test_invoicing_same_data(self):
        invoice = self.order._create_invoices()
        self.assertEqual(invoice.category_ids, self.tag)
