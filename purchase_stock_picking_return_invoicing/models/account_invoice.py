# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        """Remove lines with qty=0 when making refunds."""
        res = super().purchase_order_change()
        if self.type == 'in_refund':
            self.invoice_line_ids -= self.invoice_line_ids.filtered(
                lambda x: float_is_zero(
                    x.quantity, precision_rounding=x.uom_id.rounding,
                )
            )
        return res

    def _prepare_invoice_line_from_po_line(self, line):
        data = super()._prepare_invoice_line_from_po_line(line)
        if line.product_id.purchase_method == 'receive':
            # This formula proceeds from the simplification of full expression:
            # qty_received + qty_returned - (qty_invoiced + qty_refunded) -
            # (qty_returned - qty_refunded)
            qty = line.qty_received - line.qty_invoiced
            data['quantity'] = qty
        if self.type == 'in_refund':
            invoice_line = self.env['account.invoice.line']
            data['quantity'] *= -1.0
            data['account_id'] = invoice_line.with_context(
                {'journal_id': self.journal_id.id,
                 'type': 'in_invoice'})._default_account(),
            account = invoice_line.get_invoice_line_account(
                'in_invoice', line.product_id,
                self.purchase_id.fiscal_position_id, self.env.user.company_id)
            if account:
                data['account_id'] = account.id
        return data
