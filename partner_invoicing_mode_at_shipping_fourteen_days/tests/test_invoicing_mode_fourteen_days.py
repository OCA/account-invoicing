# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.tests.common import TransactionCase

from odoo.addons.partner_invoicing_mode_at_shipping.tests.common import (
    InvoiceModeAtShippingCommon,
)
from odoo.addons.queue_job.tests.common import trap_jobs


class TestInvoiceModeAtShippingGroupedFourteen(
    InvoiceModeAtShippingCommon, TransactionCase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.companies = cls.env["res.company"].search([])

    @freeze_time("2023-12-19")
    def test_invoice_created_at_shipping_per_delivery(self):
        """
        Today is '2023-12-19'
        Set partner to invoice per shipping
        Set next invoice date to '2023-12-21'

        Confirm sale orders and transfer pickings
        Launch the 14 days cron job

        The draft invoices should stay as draft
        """
        self.partner.next_invoice_date = "2023-12-21"
        self.partner.invoicing_mode = "fourteen_days"
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
            self.env["sale.order"].cron_generate_fourteen_days_invoices()
            trap.assert_enqueued_job(
                self.env["sale.order"]._validate_per_shipping_generated_invoices,
                args=(),
                kwargs={"companies": self.companies, "invoicing_mode": "fourteen_days"},
            )
            with trap_jobs() as trap_invoice:
                trap.perform_enqueued_jobs()
                self.assertFalse(trap_invoice.enqueued_jobs)
        self.assertEqual("draft", invoice.state)
        self.assertEqual("draft", invoice_2.state)

    @freeze_time("2023-12-21")
    def test_invoice_created_at_shipping_per_delivery_14(self):
        """
        Today is '2023-12-21'
        Set partner to invoice per shipping
        Set next invoice date to '2023-12-21'

        Confirm sale orders and transfer pickings
        Launch the 14 days cron job

        The draft invoices should stay as draft
        """
        self.partner.next_invoice_date = "2023-12-21"
        self.partner.invoicing_mode = "fourteen_days"
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
            self.env["sale.order"].cron_generate_fourteen_days_invoices()
            trap.assert_enqueued_job(
                self.env["sale.order"]._validate_per_shipping_generated_invoices,
                args=(),
                kwargs={"companies": self.companies, "invoicing_mode": "fourteen_days"},
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
