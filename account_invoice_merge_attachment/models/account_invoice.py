# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        invoices_info = super(AccountInvoice, self).do_merge(
            keep_references=keep_references, date_invoice=date_invoice)

        if self.env.context.get('link_attachment'):
            AttachmentObj = self.env['ir.attachment']
            for new_invoice_id in invoices_info:
                old_invoice_ids = invoices_info[new_invoice_id]
                attachs = AttachmentObj.search([
                    ('res_model', '=', self._name),
                    ('res_id', 'in', old_invoice_ids)
                ])
                for attach in attachs:
                    attach.copy(default={
                        'res_id': new_invoice_id,
                        'name': attach.name
                    })

        return invoices_info
