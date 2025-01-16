# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.queue_job.tests.common import trap_jobs


class TestInvoiceAtShipping(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.group_shippings = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "location_id": cls.warehouse.lot_stock_id.id,
                "product_id": cls.product.id,
                "inventory_quantity": 50.0,
            }
        )._apply_inventory()

    @classmethod
    def _create_order(cls):
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
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

    def test_invoice_at_shipping(self):
        self.partner.invoicing_mode = "at_shipping"
        self.so1 = self._create_order()
        self.so1.action_confirm()
        self.assertTrue(self.so1.picking_ids)

        self.so2 = self._create_order()
        self.so2.action_confirm()
        self.assertEqual(self.so1.picking_ids, self.so2.picking_ids)

        self.assertEqual(2, len(self.so1.picking_ids.move_ids))

        self.so2.order_line.move_ids.move_line_ids.write(
            {"qty_done": self.so2.order_line.move_ids.product_uom_qty}
        )
        with trap_jobs() as trap:
            self.so2.order_line.move_ids.picking_id._action_done()
            trap.assert_jobs_count(1)
            trap.perform_enqueued_jobs()
        self.assertEqual(self.so2.order_line.move_ids.picking_id.state, "done")
        self.assertTrue(self.so2.order_line.move_ids.picking_id.backorder_ids)
        self.assertEqual(
            self.so1.order_line.move_ids.picking_id,
            self.so2.order_line.move_ids.picking_id.backorder_ids,
        )
        self.so1.order_line.move_ids.move_line_ids.write(
            {"qty_done": self.so1.order_line.move_ids.product_uom_qty}
        )
        with trap_jobs() as trap:
            self.so1.order_line.move_ids.picking_id._action_done()
            trap.assert_jobs_count(1)
            trap.perform_enqueued_jobs()

        self.assertEqual(1, len(self.so2.invoice_ids))
        self.assertEqual(1, len(self.so1.invoice_ids))
        self.assertNotEqual(self.so2.invoice_ids, self.so1.invoice_ids)
