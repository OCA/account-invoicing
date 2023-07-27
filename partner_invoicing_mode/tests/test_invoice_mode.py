# Copyright 2022 Opener B.V.
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import TransactionCase

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import CommonPartnerInvoicingMode


class TestInvoiceModeAtShipping(CommonPartnerInvoicingMode, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cron = cls.env.ref(
            "partner_invoicing_mode.ir_cron_generate_standard_invoice"
        )

    def test_invoice_job_related_action(self):
        """Dedicated invoice view is present in queue job's multi invoice action"""
        invoice1 = self.env.ref("account.1_demo_invoice_1").copy()
        invoice2 = self.env.ref("account.1_demo_invoice_1").copy()
        job_single = self.env["queue.job"].search(
            [("uuid", "=", invoice1.with_delay()._validate_invoice().uuid)]
        )
        action_single = job_single.open_related_action()
        self.assertFalse(action_single.get("view_id"))
        job_multi = self.env["queue.job"].search(
            [("uuid", "=", (invoice1 + invoice2).with_delay()._validate_invoice().uuid)]
        )
        action_multi = job_multi.open_related_action()
        self.assertEqual(
            action_multi["view_id"], self.env.ref("account.view_out_invoice_tree").id
        )

    def test_invoicing_standard(self):
        self.so1.payment_term_id = self.pt1.id
        self._confirm_and_deliver(self.so1)
        self.assertFalse(self.so1.invoice_ids)
        with trap_jobs() as trap:
            self.SaleOrder.generate_invoices()
            for job in trap.enqueued_jobs:
                job.perform()
        self.assertTrue(self.so1.invoice_ids)
        # No errors are raised when called without anything to invoice
        with trap_jobs() as trap:
            self.SaleOrder.generate_invoices()
            trap.assert_jobs_count(0)

    def test_invoicing_standard_cron(self):
        self.so1.payment_term_id = self.pt1.id
        self._confirm_and_deliver(self.so1)
        self.assertFalse(self.so1.invoice_ids)
        with trap_jobs() as trap:
            self.cron.method_direct_trigger()
            for job in trap.enqueued_jobs:
                job.perform()
        self.assertTrue(self.so1.invoice_ids)

    def test_invoicing_standard_grouping(self):
        # Confirm and deliver both sale orders
        self._confirm_and_deliver(self.so1)
        self._confirm_and_deliver(self.so2)
        with trap_jobs() as trap:
            self.SaleOrder.generate_invoices()
            for job in trap.enqueued_jobs:
                job.perform()
        # Check one invoice is generated
        self.assertEqual(1, len(self.so2.invoice_ids))
        self.assertEqual(1, len(self.so1.invoice_ids))
        # Check the invoice is the same
        self.assertEqual(self.so2.invoice_ids, self.so1.invoice_ids)

    def test_invoicing_standard_no_grouping(self):
        # Confirm and deliver both sale orders
        self.so1.one_invoice_per_order = True
        self.so2.one_invoice_per_order = True
        self._confirm_and_deliver(self.so1)
        self._confirm_and_deliver(self.so2)
        with trap_jobs() as trap:
            self.SaleOrder.generate_invoices()
            for job in trap.enqueued_jobs:
                job.perform()
        # Check one invoice is generated
        self.assertEqual(1, len(self.so2.invoice_ids))
        self.assertEqual(1, len(self.so1.invoice_ids))
        # Check the invoice is the same
        self.assertNotEqual(self.so2.invoice_ids, self.so1.invoice_ids)
