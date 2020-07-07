# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models

from odoo.addons.queue_job.job import job


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_done(self):
        res = super().action_done()
        picking_to_invoice = self.filtered(
            lambda r: r.sale_id.partner_invoice_id.invoicing_mode == "at_shipping"
            and r.picking_type_code == "outgoing"
        )
        for picking in picking_to_invoice:
            picking.with_delay()._invoicing_at_shipping()
        return res

    @job(default_channel="root.invoice_at_shipping")
    def _invoicing_at_shipping(self):
        self.ensure_one()
        sale_order_ids = self._get_sales_order_to_invoice()
        partner = sale_order_ids.partner_invoice_id
        invoices = sale_order_ids._create_invoices(
            grouped=partner.one_invoice_per_order
        )
        for invoice in invoices:
            invoice.with_delay()._validate_invoice()
        return invoices

    def _get_sales_order_to_invoice(self):
        return self.mapped("move_lines.group_id.sale_id")
