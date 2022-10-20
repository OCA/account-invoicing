from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(
            order, name, amount, so_line
        )
        if order.receipts:
            invoice_vals["move_type"] = "out_receipt"
        return invoice_vals

    def create_invoices(self):
        action = super().create_invoices()
        # Show created receipts if something has to be shown
        if self._context.get("open_invoices", False):
            order_ids = self._context.get("active_ids", [])
            orders = self.env["sale.order"].browse(order_ids)
            if all(orders.mapped("receipts")):
                action = orders.action_view_receipt()
        return action
