# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import InvoiceModeAtShippingCommon


class TestInvoiceModeAtShipping(InvoiceModeAtShippingCommon, TransactionCase):
    def test_invoice_created_at_shipping_per_delivery(self):
        """Check that an invoice is created when goods are shipped."""
        self.partner.invoicing_mode = "standard"
        self.partner.one_invoice_per_shipping = True
        self._create_order()
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
                {"one_invoice_per_shipping": True, "invoicing_mode": "at_shipping"}
            )
        with self.assertRaises(ValidationError):
            self.partner.write(
                {"one_invoice_per_order": True, "one_invoice_per_shipping": True}
            )
