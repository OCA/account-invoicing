# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.tools import groupby


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
        SALE = self.env["sale.order"]
        sales = SALE.browse()
        # Filter out non invoicable sales order
        sales = self._get_sales_order_to_invoice()
        invoice_ids = set()
        for _partner_invoice, sale_orders in groupby(
            sales, lambda sale_order: sale_order.partner_invoice_id
        ):
            sale_order_ids = SALE.union(*sale_orders).ids
            invoice_ids = invoice_ids.union(
                set(SALE._generate_invoices_by_partner(sale_order_ids).ids)
            )
        return self.env["account.move"].browse(invoice_ids) or _("Nothing to invoice.")

    def _get_sales_order_to_invoice(self):
        return self.mapped("move_lines.sale_line_id.order_id").filtered(
            lambda r: r._get_invoiceable_lines()
        )
