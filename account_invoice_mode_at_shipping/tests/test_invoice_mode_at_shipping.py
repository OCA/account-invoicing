# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged("post_install", "-at_install")
class TestInvoiceModeAtShipping(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.so1 = cls.env["sale.order"].create(
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
        stock_location = cls.env.ref("stock.stock_location_stock")
        inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "product_ids": [(6, 0, cls.product.ids)],
                "state": "confirm",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_qty": 100,
                            "location_id": stock_location.id,
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        inventory.action_validate()

    def test_invoice_created_at_shipping(self):
        """Check that an invoice is created when goods are shipped."""
        self.partner.invoicing_mode = "at_shipping"
        self.so1.action_confirm()
        for picking in self.so1.picking_ids:
            for line in picking.move_lines:
                line.quantity_done = line.product_uom_qty
                picking.action_assign()
                picking.with_context(test_queue_job_no_delay=True).button_validate()
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(self.so1.invoice_ids.state, "posted")

    def test_invoice_not_created_at_shipping(self):
        """Check that an invoice is not created when goods are shipped."""
        self.partner.invoicing_mode = "standard"
        self.so1.action_confirm()
        for picking in self.so1.picking_ids:
            for line in picking.move_lines:
                line.quantity_done = line.product_uom_qty
            picking.action_assign()
            picking.button_validate()
        self.assertEqual(len(self.so1.invoice_ids), 0)
