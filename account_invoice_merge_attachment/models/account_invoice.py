# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        invoices_info = super(AccountInvoice, self).do_merge(
            keep_references=keep_references, date_invoice=date_invoice)
        if self.env.context.get('link_attachment'):
            attach_obj = self.env['ir.attachment']
            for new_invoice_id in invoices_info:
                attachs = attach_obj.search(
                    [('res_model', '=', 'account.invoice'),
                     ('res_id', 'in', invoices_info[new_invoice_id])])
                for attach in attachs:
                    attach.copy(default={'res_id': new_invoice_id,
                                         'name': attach.name})
        return invoices_info
