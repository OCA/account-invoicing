# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from unittest import mock

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.partner_invoicing_mode.tests.common import CommonPartnerInvoicingMode
from odoo.addons.partner_invoicing_mode_monthly.models.sale_order import SaleOrder


class TestInvoiceModeMonthly(CommonPartnerInvoicingMode, TransactionCase):

    _invoicing_mode = "monthly"

    def deliver_invoice(self, sale_order):
        sale_order.action_confirm()
        for picking in sale_order.picking_ids:
            for move in picking.move_ids:
                move.quantity_done = move.product_uom_qty
            picking.action_assign()
            picking.with_context(test_queue_job_no_delay=True).button_validate()

    def test_invoice_mode_monthly(self):
        self.so1.payment_term_id = self.pt1.id
        self.deliver_invoice(self.so1)
        self.assertFalse(self.so1.invoice_ids)
        with mute_logger("odoo.addons.queue_job.delay"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_monthly_invoices()
        self.assertTrue(self.so1.invoice_ids)
        # No errors are raised when called without anything to invoice
        with mute_logger("odoo.addons.queue_job.delay"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_monthly_invoices()

    def test_invoice_mode_monthly_cron(self):
        cron = self.env.ref(
            "partner_invoicing_mode_monthly.ir_cron_generate_monthly_invoice"
        )
        self.so1.payment_term_id = self.pt1.id
        self.deliver_invoice(self.so1)
        self.assertFalse(self.so1.invoice_ids)
        with mute_logger("odoo.addons.queue_job.delay"), mock.patch.object(
            SaleOrder,
            "_company_monthly_invoicing_today",
            return_value=self.so1.company_id,
        ):
            cron.with_context(test_queue_job_no_delay=True).ir_actions_server_id.run()
        self.assertTrue(self.so1.invoice_ids)

    def test_saleorder_with_different_mode_term(self):
        """Check multiple sale order one partner diverse terms."""
        self.so1.payment_term_id = self.pt1.id
        self.deliver_invoice(self.so1)
        self.so2.payment_term_id = self.pt2.id
        self.deliver_invoice(self.so2)
        with mute_logger("odoo.addons.queue_job.delay"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_monthly_invoices(self.company)
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        # Two invoices because the term are different
        self.assertNotEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")

    def test_saleorder_grouped_in_invoice(self):
        """Check multiple sale order grouped in one invoice"""
        self.deliver_invoice(self.so1)
        self.deliver_invoice(self.so2)
        with mute_logger("odoo.addons.queue_job.delay"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_monthly_invoices(self.company)
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        # Same invoice for both order
        self.assertEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")

    def test_split_invoice_by_sale_order(self):
        """For same customer invoice 2 sales order separately."""
        self.partner.invoicing_mode = "monthly"
        self.partner.one_invoice_per_order = True
        self.deliver_invoice(self.so1)
        self.deliver_invoice(self.so2)
        with mute_logger("odoo.addons.queue_job.delay"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_monthly_invoices(self.company)
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        # Two invoices as they must be split
        self.assertNotEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        self.assertEqual(self.so2.invoice_ids.state, "posted")

    def test_invoice_for_multiple_customer(self):
        """Check two sale order for different customers."""
        self.partner.invoicing_mode = "monthly"
        self.so2.partner_id = self.partner2
        self.so2.partner_invoice_id = self.partner2
        self.so2.partner_shipping_id = self.partner2
        self.deliver_invoice(self.so1)
        self.deliver_invoice(self.so2)
        with mute_logger("odoo.addons.queue_job.delay"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_monthly_invoices(self.company)
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        self.assertNotEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        self.assertEqual(self.so2.invoice_ids.state, "posted")
