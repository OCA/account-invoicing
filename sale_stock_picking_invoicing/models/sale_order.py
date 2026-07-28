# Copyright (C) 2020-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        lines = super()._get_invoiceable_lines(final)
        model = self.env.context.get("active_model")
        if (
            self.company_id.sale_invoicing_policy == "stock_picking"
            and model != "stock.picking"
            and lines
        ):
            so_invoiceable_lines = lines.filtered(
                lambda ln: ln.product_id.type != "consu" and not ln.is_downpayment
            )
            if so_invoiceable_lines.filtered(lambda ln: not ln.display_type):
                lines = so_invoiceable_lines
            else:
                raise UserError(
                    self.env._(
                        "When 'Sale Invoicing Policy' is defined as "
                        "'Stock Picking' the Invoice can only be created"
                        " from the Stock Picking, if necessary you can change"
                        " in the Company or Sale Settings."
                    )
                )
        return lines

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Mark related pickings as invoiced when fully invoiced from SO.

        Only applies under the 'both' policy. Under 'stock_picking' the
        SO can only invoice services (no picking to sync); under
        'sale_order' the picking is not part of the invoicing flow.
        """
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        for order in self.filtered(
            lambda o: o.company_id.sale_invoicing_policy == "both"
        ):
            for picking in order.picking_ids.filtered(
                lambda p: p.invoice_state == "2binvoiced"
            ):
                pending_moves = picking.move_ids.filtered(
                    lambda m: m.sale_line_id
                    and (
                        m.sale_line_id.qty_to_invoice > 0
                        or m.sale_line_id.qty_invoiced == 0
                        or (
                            m.sale_line_id.product_id.invoice_policy == "delivery"
                            and m.state != "done"
                        )
                    )
                )
                if not pending_moves:
                    picking.set_as_invoiced()
        return invoices
