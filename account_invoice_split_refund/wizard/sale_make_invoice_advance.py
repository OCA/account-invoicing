# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(
        selection_add=[
            ("all_split", "Invoiceable lines (Split refunds from invoices)")
        ],
        default=lambda self: self._get_advance_payment_method(),
        ondelete={"all_split": "set default"},
    )

    @api.model
    def _get_advance_payment_method(self):
        """Force splitting refunds from invoices as default method"""
        return "all_split"

    def create_invoices(self):
        if self.advance_payment_method != "all_split":
            return super().create_invoices()
        sale_orders = self.sale_order_ids
        to_invoice = sale_orders.order_line.filtered(lambda l: l.qty_to_invoice > 0)
        to_refund = sale_orders.order_line.filtered(lambda l: l.qty_to_invoice < 0)
        # Create all the invoices
        if to_invoice:
            sale_orders._create_invoices(final=False)
        # Create all the refunds
        if to_refund:
            sale_orders._create_invoices(final=True)
        # Open invoices or close the wizard according to context key
        if self._context.get("open_invoices", False):
            return sale_orders.action_view_invoice()
        return {"type": "ir.actions.act_window_close"}
