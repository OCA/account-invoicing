# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.queue_job.tests.common import trap_jobs


class TestInvoiceModeAtShipping(TransactionCase):
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

    def test_invoice_created_at_shipping_per_delivery(self):
        """Check that an invoice is created when goods are shipped."""
        self.partner.invoicing_mode = "standard"
        self.partner.one_invoice_per_picking = True
        self.so1.action_confirm()
        picking = self.so1.picking_ids

        # Deliver partially
        picking.move_ids.quantity_done = 2.0
        with trap_jobs() as trap:
            picking._action_done()
            trap.assert_enqueued_job(
                picking._invoicing_at_shipping,
            )
            trap.perform_enqueued_jobs()

        self.assertEqual(picking.state, "done")
        invoice = self.so1.invoice_ids
        # Invoice is generated but is still draft
        self.assertEqual(
            "draft",
            invoice.state,
        )

        backorder = self.so1.picking_ids - picking
        self.assertTrue(backorder)

        backorder.move_ids.quantity_done = 2.0
        with trap_jobs() as trap:
            backorder._action_done()
            trap.assert_enqueued_job(
                backorder._invoicing_at_shipping,
            )
            with trap_jobs() as trap_invoice:
                trap.perform_enqueued_jobs()
                self.assertFalse(trap_invoice.enqueued_jobs)
        invoice_2 = self.so1.invoice_ids - invoice
        self.assertEqual(
            "draft",
            invoice_2.state,
        )
        # Launch the invoicing
        with trap_jobs() as trap:
            self.env["sale.order"].cron_generate_standard_invoices()
            trap.assert_enqueued_job(
                self.env["sale.order"]._generate_invoices_by_partner,
                args=(self.so1.ids,),
            )
            with trap_jobs() as trap_invoice:
                trap.perform_enqueued_jobs()
                trap_invoice.assert_enqueued_job(
                    self.so1.invoice_ids[0]._validate_invoice
                )
                trap_invoice.assert_enqueued_job(
                    self.so1.invoice_ids[1]._validate_invoice
                )
                trap_invoice.perform_enqueued_jobs()
        self.assertEqual("posted", invoice.state)
        self.assertEqual("posted", invoice_2.state)

    def test_invoice_created_at_shipping_per_delivery_constrains(self):
        with self.assertRaises(ValidationError):
            self.partner.write(
                {"one_invoice_per_picking": True, "invoicing_mode": "at_shipping"}
            )
        with self.assertRaises(ValidationError):
            self.partner.write(
                {"one_invoice_per_order": True, "one_invoice_per_picking": True}
            )
