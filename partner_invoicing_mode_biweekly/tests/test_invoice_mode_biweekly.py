# Copyright 2026 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tools import mute_logger

from odoo.addons.partner_invoicing_mode.tests.common import CommonPartnerInvoicingMode
from odoo.addons.partner_invoicing_mode_biweekly.models.sale_order import SaleOrder


class TestInvoiceModeBiweekly(CommonPartnerInvoicingMode):
    _invoicing_mode = "biweekly"

    def deliver_invoice(self, sale_order):
        sale_order.action_confirm()
        for picking in sale_order.picking_ids:
            for move in picking.move_ids:
                move.quantity = move.product_uom_qty
            picking.action_assign()
            picking.button_validate()

    def test_invoice_mode_biweekly(self):
        self.so1.payment_term_id = self.pt1.id
        self.deliver_invoice(self.so1)
        self.assertFalse(self.so1.invoice_ids)
        with mute_logger("odoo.addons.queue_job.delay"):
            self.SaleOrder.with_context(
                queue_job__no_delay=True
            ).generate_biweekly_invoices()
        self.assertTrue(self.so1.invoice_ids)
        # No errors are raised when called without anything to invoice
        with mute_logger("odoo.addons.queue_job.delay"):
            self.SaleOrder.with_context(
                queue_job__no_delay=True
            ).generate_biweekly_invoices()

    def test_invoice_mode_biweekly_cron(self):
        cron = self.env.ref(
            "partner_invoicing_mode_biweekly.ir_cron_generate_biweekly_invoice"
        )
        self.so1.payment_term_id = self.pt1.id
        self.deliver_invoice(self.so1)
        self.assertFalse(self.so1.invoice_ids)
        with (
            mute_logger("odoo.addons.queue_job.delay"),
            mock.patch.object(
                SaleOrder,
                "_company_biweekly_invoicing_today",
                return_value=self.so1.company_id,
            ),
        ):
            cron.with_context(queue_job__no_delay=True).ir_actions_server_id.run()
        self.assertTrue(self.so1.invoice_ids)
