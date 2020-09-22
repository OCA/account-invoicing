# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models

from odoo.addons.queue_job.job import job


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_done(self):
        res = super().action_done()

        for picking in self:
            if picking._invoice_at_shipping():
                picking.with_delay()._invoicing_at_shipping()
        return res

    def _invoice_at_shipping(self):
        """Check if picking must be invoiced at shipping."""
        self.ensure_one()
        return (
            self.picking_type_code == "outgoing"
            and self.sale_id.partner_invoice_id.invoicing_mode == "at_shipping"
        )

    @job(default_channel="root.invoice_at_shipping")
    def _invoicing_at_shipping(self):
        self.ensure_one()
        sales_order = self._get_sales_order_to_invoice()
        partner = sales_order.partner_invoice_id
        invoices = sales_order._create_invoices(grouped=partner.one_invoice_per_order)
        for invoice in invoices:
            invoice.with_delay()._validate_invoice()
        return invoices

    def _get_sales_order_to_invoice(self):
        return self.mapped("move_lines.sale_line_id.order_id")
