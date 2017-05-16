# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    supplier_invoice_number = fields.Char(
        string='Vendor invoice number'
    )

    @api.multi
    def compute_refund(self, mode='refund'):
        res = True
        for form in self:
            res = super(
                AccountInvoiceRefund, form.with_context(
                    supplier_invoice_number=form.supplier_invoice_number)).\
                compute_refund(mode=mode)
        return res
