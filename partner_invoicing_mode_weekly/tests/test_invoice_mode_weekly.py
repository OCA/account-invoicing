# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from freezegun import freeze_time

from odoo import fields, tools
from odoo.tests.common import TransactionCase
from odoo.tools import relativedelta

from odoo.addons.partner_invoicing_mode.tests.common import CommonPartnerInvoicingMode
from odoo.addons.queue_job.tests.common import trap_jobs


class TestInvoiceModeWeekly(CommonPartnerInvoicingMode, TransactionCase):

    _invoicing_mode = "weekly"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cron = cls.env.ref(
            "partner_invoicing_mode_weekly.ir_cron_generate_weekly_invoice"
        )

    def test_saleorder_with_different_mode_term(self):
        """Check multiple sale order one partner diverse terms."""
        self.so1.payment_term_id = self.pt1.id
        self._confirm_and_deliver(self.so1)
        self.so2.payment_term_id = self.pt2.id
        self._confirm_and_deliver(self.so2)
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
        self._confirm_and_deliver(self.so1)
        self._confirm_and_deliver(self.so2)
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
        self._confirm_and_deliver(self.so1)
        self._confirm_and_deliver(self.so2)
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
        self._confirm_and_deliver(self.so1)
        self._confirm_and_deliver(self.so2)
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_weekly_invoices(self.company)
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        self.assertNotEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        self.assertEqual(self.so2.invoice_ids.state, "posted")

    @freeze_time("2023-05-10")
    def test_cron(self):
        # Today is Wednesday
        self.env.company.invoicing_mode_weekly_last_execution = (
            fields.Datetime.now() - relativedelta(days=10)
        )
        self.env.company.invoicing_mode_weekly_day_todo = "2"
        self.partner.invoicing_mode = "weekly"
        self.so2.partner_id = self.partner2
        self.so2.partner_invoice_id = self.partner2
        self.so2.partner_shipping_id = self.partner2
        self._confirm_and_deliver(self.so1)
        self._confirm_and_deliver(self.so2)
        with trap_jobs() as trap:
            self.env["sale.order"].cron_generate_weekly_invoices()
            trap.assert_jobs_count(2)
            trap.assert_enqueued_job(
                self.env["sale.order"]._generate_invoices_by_partner,
                args=(self.so1.ids,),
                kwargs={},
            )
            with trap_jobs() as trap_invoice:
                for job in trap.enqueued_jobs:
                    if job.args == (self.so1.ids,):
                        job.perform()
                trap_invoice.assert_jobs_count(1)
                trap_invoice.assert_enqueued_job(
                    self.so1.invoice_ids._validate_invoice,
                    args=(),
                    kwargs={},
                )
                trap_invoice.enqueued_jobs[0].perform()

            with trap_jobs() as trap_invoice:
                for job in trap.enqueued_jobs:
                    if job.args == (self.so2.ids,):
                        job.perform()
                trap_invoice.assert_jobs_count(1)
                trap_invoice.assert_enqueued_job(
                    self.so2.invoice_ids._validate_invoice,
                    args=(),
                    kwargs={},
                )
                trap_invoice.enqueued_jobs[0].perform()

        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        self.assertNotEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        self.assertEqual(self.so2.invoice_ids.state, "posted")
