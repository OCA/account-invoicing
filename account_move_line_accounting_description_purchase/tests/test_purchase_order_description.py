# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.tests.common import SavepointCase


class TestPurchaseOrderDescription(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.product_with_acc_desc = cls.env.ref("product.product_product_1")
        cls.product_without_acc_desc = cls.env.ref("product.product_product_2")

        consumable_cat = cls.env["product.category"].search(
            [("name", "=", "Consumable")]
        )

        cls.product_with_acc_desc.categ_id = consumable_cat
        cls.product_without_acc_desc.categ_id = consumable_cat

        cls.product_with_acc_desc.purchase_method = "purchase"
        cls.product_without_acc_desc.purchase_method = "purchase"

        cls.product_with_acc_desc.accounting_description = "Product1_acc_desc"

        cls.po_product_with_acc = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_with_acc_desc.id,
                            "product_qty": 5.0,
                            "product_uom": cls.product_with_acc_desc.uom_id.id,
                            "price_unit": 10,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        cls.po_product_with_acc_line = cls.po_product_with_acc.order_line
        cls.po_product_with_acc.button_confirm()
        cls.po_product_with_acc.button_approve()

        cls.po_product_without_acc = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_without_acc_desc.id,
                            "product_qty": 5.0,
                            "product_uom": cls.product_without_acc_desc.uom_id.id,
                            "price_unit": 10,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        cls.po_product_without_acc_line = cls.po_product_without_acc.order_line
        cls.po_product_without_acc.button_confirm()
        cls.po_product_without_acc.button_approve()

    def test_purchase_order_line_name(self):

        # For 1st PO check invoice line is same as product description
        action_1 = self.po_product_with_acc.action_create_invoice()
        inv_1 = self.env["account.move"].browse(action_1["res_id"])
        inv_line_with_product = inv_1.line_ids.filtered(lambda x: x.product_id)

        self.assertTrue(self.product_with_acc_desc.accounting_description)
        self.assertEqual(
            inv_line_with_product.name,
            self.product_with_acc_desc.accounting_description,
        )
        self.assertIn(
            inv_line_with_product.product_id.name, inv_line_with_product.external_name
        )

        # For 2nd PO make sure invoice line name isn't set to product description
        action_2 = self.po_product_without_acc.action_create_invoice()
        inv_2 = self.env["account.move"].browse(action_2["res_id"])
        inv_line_with_product = inv_2.line_ids.filtered(lambda x: x.product_id)

        self.assertFalse(self.product_without_acc_desc.accounting_description)
        self.assertNotEqual(
            inv_line_with_product.name,
            self.product_without_acc_desc.accounting_description,
        )
        self.assertIn(
            inv_line_with_product.product_id.name, inv_line_with_product.external_name
        )
