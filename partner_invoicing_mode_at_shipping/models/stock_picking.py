# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        for picking in self:
            if picking._invoice_at_shipping():
                delay_options = picking._get_invoicing_at_shipping_delay_options()
                picking.with_delay(**delay_options)._invoicing_at_shipping()
        return res

    def _invoice_at_shipping(self):
        """Check if picking must be invoiced at shipping."""
        self.ensure_one()
        return self.picking_type_code == "outgoing" and (
            self.sale_id.partner_invoice_id.invoicing_mode == "at_shipping"
            or self.sale_id.partner_invoice_id.one_invoice_per_shipping
        )

    def _get_invoicing_at_shipping_delay_options(self):
        """Return queue job delay options for the at shipping invoicing job."""
        self.ensure_one()
        partner = self.sale_id.partner_invoice_id
        if partner.invoicing_mode != "at_shipping":
            return {}
        delay = partner.invoicing_at_shipping_delay
        return {"eta": timedelta(days=delay)} if delay else {}

    def _invoicing_at_shipping_validation(self, invoices):
        return invoices.filtered(
            lambda invoice: invoice.partner_id.invoicing_mode == "at_shipping"
        )

    @api.model
    def _invoicing_at_shipping(self):
        self.ensure_one()
        sales = self._get_sales_order_to_invoice()
        # Split invoice creation on partner sales grouping on invoice settings
        sales_one_invoice_per_order = sales.filtered(
            "partner_invoice_id.one_invoice_per_order"
        )
        invoices = self.env["account.move"]
        if sales_one_invoice_per_order:
            invoices |= sales_one_invoice_per_order.sudo()._create_invoices(
                grouped=True
            )
        sales_many_invoice_per_order = sales - sales_one_invoice_per_order
        if sales_many_invoice_per_order:
            invoices |= sales_many_invoice_per_order.sudo()._create_invoices(
                grouped=False
            )
        # The invoices per picking will use the invoicing_mode
        for invoice in self._invoicing_at_shipping_validation(invoices):
            invoice.with_delay()._validate_invoice()
        return invoices or self.env._("Nothing to invoice.")

    def _get_sales_order_to_invoice(self):
        return self.move_ids.sale_line_id.order_id.filtered(
            lambda r: r._get_invoiceable_lines()
        )
