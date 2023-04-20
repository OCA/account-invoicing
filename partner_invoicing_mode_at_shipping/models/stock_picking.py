# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
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

    def _invoicing_at_shipping(self):
        self.ensure_one()
        sales = self.env["sale.order"].browse()
        # Filter out non invoicable sales order
        for sale in self._get_sales_order_to_invoice():
            if sale._get_invoiceable_lines():
                sales |= sale
        # Split invoice creation on partner sales grouping on invoice settings
        sales_one_invoice_per_order = sales.filtered(
            "partner_invoice_id.one_invoice_per_order"
        )
        invoices = self.env["account.move"].browse()
        if sales_one_invoice_per_order:
            invoices |= sales_one_invoice_per_order._create_invoices(grouped=True)
        sales_many_invoice_per_order = sales - sales_one_invoice_per_order
        if sales_many_invoice_per_order:
            invoices |= sales_many_invoice_per_order._create_invoices(grouped=False)
        for invoice in invoices:
            invoice.with_delay()._validate_invoice()
        return invoices or _("Nothing to invoice.")

    def _get_sales_order_to_invoice(self):
        return self.mapped("move_lines.sale_line_id.order_id").filtered(
            lambda r: r._get_invoiceable_lines()
        )
