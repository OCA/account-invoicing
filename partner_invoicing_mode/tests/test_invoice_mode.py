# Copyright 2022 Opener B.V.
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from unittest import mock

from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.queue_job.tests.common import trap_jobs

from ..models.res_partner import ResPartner
from .common import CommonPartnerInvoicingMode


class TestInvoiceMode(CommonPartnerInvoicingMode, TransactionCase):
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

    def test_grouping_change(self):
        # Create a sale order with a partner that have one invoice per order enabled
        # Check if the sale order created has that option enabled
        # Change the partner, then check if the option is disabled
        # Then, set it manually and check if value remains.
        self.partner2.one_invoice_per_order = True
        so3 = self.so1.copy()
        so3.partner_id = self.partner2
        self.assertTrue(so3.one_invoice_per_order)
        so3.partner_id = self.partner
        self.assertFalse(so3.one_invoice_per_order)
        so3.one_invoice_per_order = True
        self.assertTrue(so3.one_invoice_per_order)

    def test_update_date(self):
        # Check the update next invoice date function has been called
        with mock.patch.object(ResPartner, "_update_next_invoice_date") as mock_update:
            self._confirm_and_deliver(self.so1)
            with trap_jobs() as trap:
                self.SaleOrder.generate_invoices()
                for job in trap.enqueued_jobs:
                    job.perform()
            mock_update.assert_called()

    @freeze_time("2024-03-10")
    def test_invoicing_standard_cron_invoice_date(self):
        """
        - Generate the invoice at day one
        - Execute the validation job at day two
        - Check the invoice date is day one
        """
        self.so1.payment_term_id = self.pt1.id
        self._confirm_and_deliver(self.so1)
        self.assertFalse(self.so1.invoice_ids)
        with trap_jobs() as trap:
            self.cron.method_direct_trigger()
            for job in trap.enqueued_jobs:
                with trap_jobs() as trap_validate:
                    job.perform()
                self.assertEqual(1, len(trap_validate.enqueued_jobs))
                for validate_job in trap_validate.enqueued_jobs:
                    with freeze_time("2024-03-11"):
                        validate_job.perform()
        self.assertTrue(self.so1.invoice_ids)
        self.assertEqual(
            fields.Date.from_string("2024-03-10"), self.so1.invoice_ids.date
        )

    def test_invoicing_standard_grouping_partner_invoicing(self):
        # Activate the ability to define a different invoice address
        # Create a new partner for invoicing
        self.env.user.groups_id |= self.env.ref(
            "account.group_delivery_invoice_address"
        )
        self.partner_invoice = self.env["res.partner"].create(
            {"name": "Partner Invoicing"}
        )
        self._confirm_and_deliver(self.so1)
        with Form(self.so2) as so2_form:
            so2_form.partner_invoice_id = self.partner_invoice
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

    def test_invoicing_standard_grouping_payment_term_invoicing(self):
        # Activate the ability to define a different payment term
        self.env.user.groups_id |= self.env.ref(
            "account.group_delivery_invoice_address"
        )
        self._confirm_and_deliver(self.so1)
        with Form(self.so2) as so2_form:
            so2_form.payment_term_id = self.env.ref(
                "account.account_payment_term_21days"
            )
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
