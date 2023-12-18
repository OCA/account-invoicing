# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from .common import InvoiceModeAtShippingCommon


class TestInvoiceModeAtShipping(InvoiceModeAtShippingCommon, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_order()

    def test_invoice_created_at_shipping(self):
        """Check that an invoice is created when goods are shipped."""
        self.partner.invoicing_mode = "at_shipping"
        self.so1.action_confirm()
        for picking in self.so1.picking_ids:
            for move in picking.move_ids:
                move.quantity_done = move.product_uom_qty
            picking.action_assign()
            with mute_logger("odoo.addons.queue_job.delay"):
                picking.with_context(test_queue_job_no_delay=True).button_validate()
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(self.so1.invoice_ids.state, "posted")

    def test_invoice_not_created_at_shipping(self):
        """Check that an invoice is not created when goods are shipped."""
        self.partner.invoicing_mode = "standard"
        self.so1.action_confirm()
        for picking in self.so1.picking_ids:
            for move in picking.move_ids:
                move.quantity_done = move.product_uom_qty
            picking.action_assign()
            with mute_logger("odoo.addons.queue_job.delay"):
                picking.with_context(test_queue_job_no_delay=True).button_validate()
        self.assertEqual(len(self.so1.invoice_ids), 0)

    def test_picking_multi_order_single_invoice(self):
        """A picking for more than one sale order creating a single invoice"""
        self.partner.invoicing_mode = "at_shipping"
        self.partner.one_invoice_per_order = False
        so2 = self.so1.copy()
        for order in self.so1, so2:
            order.action_confirm()
        # Effectively merge both pickings
        picking = self.so1.picking_ids
        so2.picking_ids.move_ids.picking_id = picking
        # Transfer the remaining picking with moves
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty
        picking.action_assign()
        with mute_logger("odoo.addons.queue_job.delay"):
            picking.with_context(test_queue_job_no_delay=True).button_validate()
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        self.assertEqual(self.so1.invoice_ids, so2.invoice_ids)

    def test_picking_multi_order_multi_invoice(self):
        """A picking for more than one sale order creates more than one invoice"""
        self.partner.invoicing_mode = "at_shipping"
        self.partner.one_invoice_per_order = True
        so2 = self.so1.copy()
        for order in self.so1, so2:
            order.action_confirm()
        # Effectively merge both pickings
        picking = self.so1.picking_ids
        so2.picking_ids.move_ids.picking_id = picking
        # Transfer the remaining picking with moves
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty
        picking.action_assign()
        with mute_logger("odoo.addons.queue_job.delay"):
            picking.with_context(test_queue_job_no_delay=True).button_validate()
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        self.assertEqual(len(so2.invoice_ids), 1)
        self.assertEqual(so2.invoice_ids.state, "posted")
        self.assertNotEqual(self.so1.invoice_ids, so2.invoice_ids)

    def test_picking_backorder(self):
        """In case of a backorder, another invoice is created"""
        self.partner.invoicing_mode = "at_shipping"
        self.so1.action_confirm()
        picking = self.so1.picking_ids
        picking.move_ids.quantity_done = 2
        picking.action_assign()
        with mute_logger("odoo.addons.queue_job.delay"):
            picking.with_context(
                skip_backorder=True, test_queue_job_no_delay=True
            ).button_validate()
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        # Now process the backorder
        backorder = self.so1.picking_ids - picking
        backorder.move_ids.quantity_done = 2
        backorder.action_assign()
        with mute_logger("odoo.addons.queue_job.delay"):
            backorder.with_context(test_queue_job_no_delay=True).button_validate()
        self.assertEqual(len(self.so1.invoice_ids), 2)
        self.assertTrue(
            all(invoice.state == "posted") for invoice in self.so1.invoice_ids
        )
