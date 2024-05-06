from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoices(self, sale_orders):
        invoice = super()._create_invoices(sale_orders)
        for sale in sale_orders:
            if sale.is_claim:
                invoices = sale.origin_order_id.invoice_ids.filtered(
                    lambda i: i.move_type != "out_refund"
                )
                move_to_ref = self.env["account.move"].search(
                    [("id", "in", invoices.ids)], order="amount_total desc", limit=1
                )
                invoice.reversed_entry_id = move_to_ref.id
        return invoice
