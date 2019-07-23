# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(
        selection_add=[
            ('all_split', 'Invoiceable lines (Split refunds from invoices)')
        ],
        default=lambda self: self._get_advance_payment_method(),
    )

    @api.model
    def _get_advance_payment_method(self):
        """Force splitting refunds from invoices as default method"""
        return 'all_split'

    @api.multi
    def create_invoices(self):
        if self.advance_payment_method != 'all_split':
            return super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        qties_to_invoice = sale_orders.mapped('order_line.qty_to_invoice')
        to_invoice = bool(filter(lambda qty: qty > 0, qties_to_invoice))
        to_refund = bool(filter(lambda qty: qty < 0, qties_to_invoice))
        # Create all the invoices
        if to_invoice:
            sale_orders.action_invoice_create()
        # Create all the refunds
        if to_refund:
            sale_orders.action_invoice_create(final=True)
        # Open invoices or close the wizard according to context key
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
