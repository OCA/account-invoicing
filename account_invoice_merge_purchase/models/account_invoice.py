# -*- coding: utf-8 -*-
# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_invoice_line_key_cols(self):
        res = super(AccountInvoice, self)._get_invoice_line_key_cols()
        res.append('purchase_line_id')
        return res

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        invoices_info = super(AccountInvoice, self).do_merge(
            keep_references=keep_references,
            date_invoice=date_invoice,
        )
        invoice_line_obj = self.env['account.invoice.line']
        todos = self.env['purchase.order']
        for new_invoice_id in invoices_info:
            for invoice in self:
                todos |= invoice.invoice_line_ids.mapped('purchase_id')
                todos.write({'invoice_ids': [(4, new_invoice_id)]})
                for org_po in todos:
                    for po_line in org_po.order_line:
                        invoice_line_ids = invoice_line_obj.search(
                            [('product_id', '=', po_line.product_id.id),
                             ('invoice_id', '=', new_invoice_id)])
                        if invoice_line_ids:
                            po_line.write(
                                {'invoice_lines': [
                                    (6, 0, invoice_line_ids.ids)]})
        return invoices_info
