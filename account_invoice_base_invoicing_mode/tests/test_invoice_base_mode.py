# Copyright 2021 Camptocamp SA
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import tools
from odoo.tests import tagged

from .common import TestInvoiceModeCommon


@tagged("post_install", "-at_install")
class TestInvoiceModeBase(TestInvoiceModeCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner.invoicing_mode = "standard"
        cls.partner2.invoicing_mode = "standard"

    def test_saleorder_with_different_mode_term(self):
        """Check multiple sale order one partner diverse terms."""
        self.so1.payment_term_id = self.pt1.id
        self.deliver_invoice(self.so1)
        self.so2.payment_term_id = self.pt2.id
        self.deliver_invoice(self.so2)
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_invoices_by_invoice_mode(
                self.company,
                "standard",
                ["partner_invoice_id", "payment_term_id"],
                "write_date",
            )
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)
        # Two invoices because the term are different
        self.assertNotEqual(self.so1.invoice_ids, self.so2.invoice_ids)
        self.assertEqual(self.so1.invoice_ids.state, "posted")

    def test_no_invoiceable_sale_orders(self):
        result = self.SaleOrder._generate_invoices_by_partner(self.so1.ids)
        self.assertEqual(result, "No sale order found to invoice ?")

    def test_no_invoice_mode(self):
        result = self.SaleOrder.generate_invoices_by_invoice_mode()
        self.assertFalse(result)

    def test_create_invoices_only_for_orders_company(self):
        self.so1.payment_term_id = self.pt1.id
        self.deliver_invoice(self.so1)
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.so1.with_context(
                test_queue_job_no_delay=True
            ).generate_invoices_by_invoice_mode(
                companies=None,
                invoice_mode="standard",
                groupby=["partner_invoice_id", "payment_term_id"],
                last_execution_field_name="write_date",
            )
        self.assertEqual(len(self.so1.invoice_ids), 1)
