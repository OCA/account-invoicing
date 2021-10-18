# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.tests.common import SavepointCase


class TestPurchaseOrderDescription(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_2 = cls.env.ref("product.product_product_2")

        consumable_cat = cls.env["product.category"].search(
            [("name", "=", "Consumable")]
        )

        cls.product_1.categ_id = consumable_cat
        cls.product_2.categ_id = consumable_cat

        cls.product_1.purchase_method = "purchase"
        cls.product_2.purchase_method = "purchase"

        cls.product_1.accounting_description = "Product1_acc_desc"

        cls.po_1 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "product_qty": 5.0,
                            "product_uom": cls.product_1.uom_id.id,
                            "price_unit": 10,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        cls.po_1_line = cls.po_1.order_line
        cls.po_1.button_confirm()
        cls.po_1.button_approve()

        cls.po_2 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_2.id,
                            "product_qty": 5.0,
                            "product_uom": cls.product_2.uom_id.id,
                            "price_unit": 10,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        cls.po_2_line = cls.po_2.order_line
        cls.po_2.button_confirm()
        cls.po_2.button_approve()

    def test_purchase_order_line_name(self):

        # For 1st PO check invoice line is same as product description
        action_1 = self.po_1.action_create_invoice()
        inv_1 = self.env["account.move"].browse(action_1["res_id"])
        inv_line_with_product = inv_1.line_ids.filtered(lambda x: x.product_id)

        self.assertTrue(self.product_1.accounting_description)
        self.assertEqual(
            inv_line_with_product.name, self.product_1.accounting_description
        )
        self.assertIn(
            inv_line_with_product.product_id.name, inv_line_with_product.external_name
        )

        # For 2nd PO make sure invoice line name isn't set to product description
        action_2 = self.po_2.action_create_invoice()
        inv_2 = self.env["account.move"].browse(action_2["res_id"])
        inv_line_with_product = inv_2.line_ids.filtered(lambda x: x.product_id)

        self.assertFalse(self.product_2.accounting_description)
        self.assertNotEqual(
            inv_line_with_product.name, self.product_2.accounting_description
        )
        self.assertIn(
            inv_line_with_product.product_id.name, inv_line_with_product.external_name
        )
