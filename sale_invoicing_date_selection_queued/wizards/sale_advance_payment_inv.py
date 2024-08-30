# © 2024 FactorLibre - Sergio Bustamante <sergio.bustamante@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def enqueue_invoices(self):
        res = super().enqueue_invoices()
        self.after_enqueued(self.invoice_date)
        return res

    def after_enqueued(self, date):
        context = self.env.context
        sale_orders = self.env["sale.order"].browse(context.get("active_ids", []))
        job_ids = self.env["queue.job"]
        for sale in sale_orders:
            job_ids |= sale.invoicing_job_ids[-1]
        self.env["sale.order.invoice.date"].create(
            {
                "sale_order_ids": sale_orders.ids,
                "job_ids": job_ids,
                "invoice_date": date,
            }
        )
