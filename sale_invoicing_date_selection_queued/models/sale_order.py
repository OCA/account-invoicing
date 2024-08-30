# © 2024 FactorLibre - Sergio Bustamante <sergio.bustamante@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def create_invoices_job(self, final):
        job_ids = self.env["queue.job"]
        for sale in self:
            job_ids |= sale.invoicing_job_ids.sorted(lambda o: o.date_created)[-1]
        bridge = self.env["sale.order.invoice.date"].search(
            [("sale_order_ids", "in", self.ids), ("job_ids", "in", job_ids.ids)]
        )
        if bridge:
            ctx = self.env.context.copy()
            ctx.update({"default_invoice_date": bridge.invoice_date})
            return super(SaleOrder, self.with_context(**ctx))._create_invoices(
                final=final
            )
        return super()._create_invoices(final=final)


class SaleOrderInvoiceDate(models.TransientModel):
    _name = "sale.order.invoice.date"

    sale_order_ids = fields.Many2many("sale.order")
    job_ids = fields.Many2many("queue.job")
    invoice_date = fields.Date()
