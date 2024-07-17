# Copyright 2021 Camptocamp SA
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import tools
from odoo.tests import tagged

from odoo.addons.account_invoice_base_invoicing_mode.tests.common import (
    TestInvoiceModeCommon,
)


@tagged("post_install", "-at_install")
class TestInvoiceModeWeekly(TestInvoiceModeCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner.invoicing_mode = "weekly"
        cls.partner2.invoicing_mode = "weekly"

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
