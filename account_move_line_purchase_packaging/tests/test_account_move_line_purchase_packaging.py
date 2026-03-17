# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.account_move_line_packaging.tests.test_account_move_line_packaging import (
    TestAccountMoveLinePackaging,
)


class TestAccountMoveLinePurchasePackaging(TestAccountMoveLinePackaging):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.packaging.purchase = True
        cls.product.purchase_method = "purchase"
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.display_name,
                            "product_id": cls.product.id,
                            "product_qty": 72.0,
                            "product_uom": cls.uom_unit.id,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        cls.po_line = cls.po.order_line

    def test_purchase_line_prepares_invoice_line_without_packaging(self):
        self.po_line.write(
            {
                "product_packaging_id": False,
                "product_packaging_qty": 0,
            }
        )
        self.po.button_confirm()
        self.po.action_create_invoice()
        bill = self.po.invoice_ids
        line = bill.invoice_line_ids
        self.assertFalse(line.product_packaging_id)
        self.assertFalse(line.product_packaging_qty)

    def test_purchase_line_prepares_invoice_line_with_packaging(self):
        self.po_line.write(
            {
                "product_packaging_id": self.packaging.id,
                "product_packaging_qty": 1.0,
            }
        )
        self.po.button_confirm()
        self.po.action_create_invoice()
        bill = self.po.invoice_ids
        line = bill.invoice_line_ids
        self.assertEqual(line.product_packaging_id, self.packaging)
        self.assertEqual(line.product_packaging_qty, 1.0)

    def test_purchase_invoice_domain_contains_purchase_flag(self):
        bill = self._create_invoice()
        line = bill.invoice_line_ids
        domain = line._get_product_packaging_domain()
        self.assertIn(("product_id", "=", self.product.id), domain)
        self.assertIn(("purchase", "=", True), domain)
