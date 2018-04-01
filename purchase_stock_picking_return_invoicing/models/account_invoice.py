# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import models
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountInvoice,
                     self)._prepare_invoice_line_from_po_line(line)
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
