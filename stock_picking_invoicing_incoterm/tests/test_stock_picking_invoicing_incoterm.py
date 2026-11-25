# Copyright 2026 Shamnas Koyani
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestStockPickingInvoicingIncoterm(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.incoterm = cls.env["account.incoterms"].search([], limit=1)
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu", "is_storable": True}
        )

    def _create_sale_order(self, incoterm=None):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "incoterm": incoterm.id if incoterm else False,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    ),
                ],
            }
        )

    def test_incoterm_propagates_from_sale_order(self):
        self.assertTrue(
            self.incoterm, "An account.incoterms record is required for this test."
        )
        sale = self._create_sale_order(incoterm=self.incoterm)
        sale.action_confirm()
        self.assertTrue(sale.picking_ids, "Sale confirmation should create a picking.")
        self.assertEqual(sale.picking_ids[:1].incoterm, self.incoterm)

    def test_incoterm_empty_when_sale_has_none(self):
        sale = self._create_sale_order(incoterm=None)
        sale.action_confirm()
        self.assertTrue(sale.picking_ids)
        self.assertFalse(sale.picking_ids[:1].incoterm)
