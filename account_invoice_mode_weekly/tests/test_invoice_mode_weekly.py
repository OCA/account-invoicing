# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import tools
from odoo.tests.common import SavepointCase


class TestInvoiceModeWeekly(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.SaleOrder = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.invoicing_mode = "weekly"
        cls.partner2 = cls.env.ref("base.res_partner_2")
        cls.partner2.invoicing_mode = "weekly"
        cls.product = cls.env.ref("product.product_delivery_01")
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

    def deliver_invoice(self, sale_order):
        sale_order.action_confirm()
        for picking in sale_order.picking_ids:
            for line in picking.move_lines:
                line.quantity_done = line.product_uom_qty
            picking.action_assign()
            picking.button_validate()

    def test_saleorder_with_different_mode_term(self):
        """Check multiple sale order one partner diverse terms."""
        self.so1.payment_term_id = self.pt1.id
        self.deliver_invoice(self.so1)
        self.so2.payment_term_id = self.pt2.id
        self.deliver_invoice(self.so2)
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_weekly_invoices(self.company)
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        # Two invoices because the term are different
        self.assertNotEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")

    def test_saleorder_grouped_in_invoice(self):
        """Check multiple sale order grouped in one invoice"""
        self.deliver_invoice(self.so1)
        self.deliver_invoice(self.so2)
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_weekly_invoices(self.company)
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        # Same invoice for both order
        self.assertEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")

    def test_split_invoice_by_sale_order(self):
        """For same customer invoice 2 sales order separately."""
        self.partner.invoicing_mode = "weekly"
        self.partner.one_invoice_per_order = True
        self.deliver_invoice(self.so1)
        self.deliver_invoice(self.so2)
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_weekly_invoices(self.company)
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        # Two invoices as they must be split
        self.assertNotEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        self.assertEqual(self.so2.invoice_ids.state, "posted")

    def test_invoice_for_multiple_customer(self):
        """Check two sale order for different customers."""
        self.partner.invoicing_mode = "weekly"
        self.so2.partner_id = self.partner2
        self.so2.partner_invoice_id = self.partner2
        self.so2.partner_shipping_id = self.partner2
        self.deliver_invoice(self.so1)
        self.deliver_invoice(self.so2)
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_weekly_invoices(self.company)
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        self.assertNotEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        self.assertEqual(self.so2.invoice_ids.state, "posted")
