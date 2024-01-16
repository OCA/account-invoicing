# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.fields import Datetime
from odoo.tests.common import TransactionCase

from odoo.addons.partner_invoicing_mode.tests.common import CommonPartnerInvoicingMode
from odoo.addons.queue_job.tests.common import trap_jobs


class TestInvoiceModeTenDays(CommonPartnerInvoicingMode, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner.invoicing_mode = "ten_days"
        cls.partner2.invoicing_mode = "ten_days"

    def test_invoice_mode(self):
        """
        Try to invoice the concerned sale orders
        """
        self._confirm_and_deliver(self.so1)
        self.assertFalse(self.so1.invoice_ids)
        with trap_jobs() as trap:
            self.SaleOrder.generate_ten_days_invoices()
            trap.assert_jobs_count(1)
            trap.enqueued_jobs[0].perform()
        self.assertTrue(self.so1.invoice_ids)

    def test_invoice_mode_ten_days_only(self):
        """
        Try to invoice the concerned sale orders
        """
        self.partner2.invoicing_mode = "standard"
        so3 = self.so2.copy(
            {
                "partner_id": self.partner2.id,
                "partner_invoice_id": self.partner2.id,
                "partner_shipping_id": self.partner2.id,
            }
        )
        self._confirm_and_deliver(self.so1)
        self._confirm_and_deliver(so3)
        self.assertFalse(self.so1.invoice_ids)
        self.assertFalse(so3.invoice_ids)
        with trap_jobs() as trap:
            self.SaleOrder.generate_ten_days_invoices()
            trap.assert_jobs_count(1)
            trap.enqueued_jobs[0].perform()
        self.assertTrue(self.so1.invoice_ids)
        self.assertFalse(so3.invoice_ids)

    def test_cron(self):
        with freeze_time("2023-06-01"):
            self._confirm_and_deliver(self.so1)
        with freeze_time("2023-06-10"):
            with trap_jobs() as trap:
                self.env["sale.order"].cron_generate_ten_days_invoices()
                trap.assert_jobs_count(1)
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
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(self.so1.invoice_ids.state, "posted")
        self.assertEqual(
            self.so1.partner_invoice_id.next_invoice_date,
            Datetime.from_string("2023-06-20"),
        )

        with freeze_time("2023-06-12"):
            so3 = self.so1.copy()
            self._confirm_and_deliver(so3)
        with freeze_time("2023-06-20"):
            with trap_jobs() as trap:
                self.env["sale.order"].cron_generate_ten_days_invoices()
                trap.assert_jobs_count(1)
                trap.assert_enqueued_job(
                    self.env["sale.order"]._generate_invoices_by_partner,
                    args=(so3.ids,),
                    kwargs={},
                )
                with trap_jobs() as trap_invoice:
                    for job in trap.enqueued_jobs:
                        if job.args == (so3.ids,):
                            job.perform()
                    trap_invoice.assert_jobs_count(1)
                    trap_invoice.assert_enqueued_job(
                        so3.invoice_ids._validate_invoice,
                        args=(),
                        kwargs={},
                    )
                    trap_invoice.enqueued_jobs[0].perform()
        self.assertEqual(len(so3.invoice_ids), 1)
        self.assertEqual(so3.invoice_ids.state, "posted")
        self.assertEqual(
            so3.partner_invoice_id.next_invoice_date, Datetime.from_string("2023-06-30")
        )

        with freeze_time("2023-06-23"):
            so4 = self.so1.copy()
            self._confirm_and_deliver(so4)
        with freeze_time("2023-06-30"):
            with trap_jobs() as trap:
                self.env["sale.order"].cron_generate_ten_days_invoices()
                trap.assert_jobs_count(1)
                trap.assert_enqueued_job(
                    self.env["sale.order"]._generate_invoices_by_partner,
                    args=(so4.ids,),
                    kwargs={},
                )
                with trap_jobs() as trap_invoice:
                    for job in trap.enqueued_jobs:
                        if job.args == (so4.ids,):
                            job.perform()
                    trap_invoice.assert_jobs_count(1)
                    trap_invoice.assert_enqueued_job(
                        so4.invoice_ids._validate_invoice,
                        args=(),
                        kwargs={},
                    )
                    trap_invoice.enqueued_jobs[0].perform()
        self.assertEqual(len(so4.invoice_ids), 1)
        self.assertEqual(so4.invoice_ids.state, "posted")
        self.assertEqual(
            so4.partner_invoice_id.next_invoice_date, Datetime.from_string("2023-07-10")
        )

    def test_cron_no(self):
        """
        The last date of execution is on 31th of May
        Create the invoice on first day of June
        Then, try to run cron on the 9th
        No invoice should be generated
        """
        with freeze_time("2023-05-31"):
            self.env.company.invoicing_mode_ten_days_last_execution = Datetime.now()
        with freeze_time("2023-06-01"):
            self._confirm_and_deliver(self.so1)
        with freeze_time("2023-05-09"):
            with trap_jobs() as trap:
                self.env["sale.order"].cron_generate_ten_days_invoices()
                trap.assert_jobs_count(0)
        self.assertEqual(len(self.so1.invoice_ids), 0)

    def test_cron_last_execution_time_agnostic(self):
        with freeze_time("2023-05-01"):
            self._confirm_and_deliver(self.so1)
        with freeze_time("2023-05-10 10:00:00"):
            self.env.company.invoicing_mode_ten_days_last_execution = Datetime.now()
        # the job for the 10th of May should not be executed since the last execution
        # is on the 10th of May
        with freeze_time("2023-05-10 11:00:01"):
            with trap_jobs() as trap:
                self.env["sale.order"].cron_generate_ten_days_invoices()
                trap.assert_jobs_count(0)
        # The 20th of May is the next invoicing date so the job should be executed
        with freeze_time("2023-05-20 10:00:01"):
            with trap_jobs() as trap:
                self.env["sale.order"].cron_generate_ten_days_invoices()
                trap.assert_jobs_count(1)

        # If a new sale order is created after the last execution, it should be invoiced
        # on the next invoicing date even if has been created the same day as the last
        # execution
        with freeze_time("2023-05-20 10:00:01"):
            so3 = self.so1.copy()
            self._confirm_and_deliver(so3)
        with freeze_time("2023-05-20 10:00:02"):
            with trap_jobs() as trap:
                self.env["sale.order"].cron_generate_ten_days_invoices()
                trap.assert_jobs_count(0)
