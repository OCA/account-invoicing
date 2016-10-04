# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_invoice_line_key_cols(self):
        res = super(AccountInvoice, self)._get_invoice_line_key_cols()
        res.append('move_line_ids')
        return res

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        invoices_info = super(AccountInvoice, self).do_merge(
            keep_references=keep_references, date_invoice=date_invoice)
        stock_picking_obj = self.env['stock.picking']
        for new_invoice_id in invoices_info:
            todos = stock_picking_obj.search(
                [('invoice_ids', 'in', invoices_info[new_invoice_id])])
            todos.write({'invoice_ids': [(4, new_invoice_id)],
                         'invoice_state': 'invoiced'})
        return invoices_info
