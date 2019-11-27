# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestSaleOrderInvoicingGroupingCriteria(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Other partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "service", "invoice_policy": "order"}
        )
        cls.GroupingCriteria = cls.env["sale.invoicing.grouping.criteria"]
        cls.grouping_criteria = cls.GroupingCriteria.create(
            {
                "name": "Delivery Address",
                "field_ids": [
                    (4, cls.env.ref("sale.field_sale_order__partner_shipping_id").id)
                ],
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
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
        cls.order2 = cls.order.copy()
        cls.order2.action_confirm()

    def test_invoicing_same_data(self):
        invoice_ids = (self.order + self.order2).action_invoice_create()
        self.assertEqual(len(invoice_ids), 1)
        self.assertEqual(self.order.invoice_ids, self.order2.invoice_ids)

    def test_invoicing_grouping_default(self):
        self.order2.partner_invoice_id = self.partner2.id
        invoice_ids = (self.order + self.order2).action_invoice_create()
        self.assertEqual(len(invoice_ids), 2)
        self.assertNotEqual(self.order.invoice_ids, self.order2.invoice_ids)

    def test_invoicing_grouping_company_criteria(self):
        self.order2.partner_shipping_id = self.partner2.id
        self.order.company_id.default_sale_invoicing_grouping_criteria_id = (
            self.grouping_criteria.id
        )
        invoice_ids = (self.order + self.order2).action_invoice_create()
        self.assertEqual(len(invoice_ids), 2)
        self.assertNotEqual(self.order.invoice_ids, self.order2.invoice_ids)

    def test_invoicing_grouping_partner_criteria(self):
        self.order2.partner_shipping_id = self.partner2.id
        self.partner.sale_invoicing_grouping_criteria_id = self.grouping_criteria.id
        invoice_ids = (self.order + self.order2).action_invoice_create()
        self.assertEqual(len(invoice_ids), 2)
        self.assertNotEqual(self.order.invoice_ids, self.order2.invoice_ids)
