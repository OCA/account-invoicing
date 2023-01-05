# Copyright 2023 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.fields import Date
from odoo.tests import TransactionCase


class MoveReversalCase(TransactionCase):
    def _reverse(self, invoice, keep_invoiced_quantities=True):
        """Actually reverse the invoice"""
        self.env["account.move.reversal"].with_context(
            active_id=invoice.id,
            active_ids=invoice.ids,
            active_model=invoice._name,
        ).create(
            {
                "refund_method": "refund",
                "keep_invoiced_quantities": keep_invoiced_quantities,
            }
        ).reverse_moves()

    def _confirm_purchase_invoice_reverse(self, purchase):
        """
        Process a purchase order, reversing its invoice keeping invoiced quantities.
        """
        purchase.button_confirm()
        purchase.button_approve()
        for line in purchase.order_line:
            self.assertEqual(line.qty_to_invoice, line.product_qty)
        purchase.action_create_invoice()
        invoice = purchase.invoice_ids
        invoice.invoice_date = Date.context_today(self.env.user)
        self.assertTrue(invoice)
        invoice.action_post()
        for line in purchase.order_line:
            self.assertFalse(line.qty_to_invoice)
        self._reverse(invoice, keep_invoiced_quantities=True)
        for line in purchase.order_line:
            self.assertFalse(line.qty_to_invoice)

    def _confirm_sale_invoice_reverse(self, sale):
        """
        Process a sales order, reversing its invoice keeping invoiced quantities.
        """
        sale.action_confirm()
        for line in sale.order_line:
            self.assertEqual(line.qty_to_invoice, line.product_uom_qty)
        invoice = sale._create_invoices()
        self.assertTrue(invoice)
        invoice.action_post()
        for line in sale.order_line:
            self.assertFalse(line.qty_to_invoice)
        self._reverse(invoice, keep_invoiced_quantities=True)
        for line in sale.order_line:
            self.assertFalse(line.qty_to_invoice)
