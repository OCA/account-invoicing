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
        invoices_info, invoice_lines_info = super(
            AccountInvoice, self).do_merge(keep_references=keep_references,
                                           date_invoice=date_invoice)
        po_obj = self.env['purchase.order']
        for new_invoice_id in invoices_info:
            todos = po_obj.search(
                [('invoice_ids', 'in', invoices_info[new_invoice_id])])
            todos.write({'invoice_ids': [(4, new_invoice_id)]})
            for org_po in todos:
                for po_line in org_po.order_line:
                    org_ilines = po_line.mapped('invoice_lines')
                    invoice_line_ids = []
                    for org_iline in org_ilines:
                        if org_iline.id in invoice_lines_info[new_invoice_id]:
                            invoice_line_ids.append(
                                invoice_lines_info[
                                    new_invoice_id][org_iline.id])
                    po_line.write(
                        {'invoice_lines': [(6, 0, invoice_line_ids)]})
                    for stock_move in po_line.move_ids:
                        stock_move.invoice_state = 'invoiced'
        return invoices_info, invoice_lines_info
