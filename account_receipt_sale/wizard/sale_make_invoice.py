from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, so_lines, accounts):
        invoice_vals = super()._prepare_invoice_values(order, so_lines, accounts)
        if order.receipts:
            invoice_vals["move_type"] = "out_receipt"
        return invoice_vals

    def create_invoices(self):
        action = super().create_invoices()
        orders = self.sale_order_ids
        if orders and all(orders.mapped("receipts")):
            action = orders.action_view_receipt()
        return action
