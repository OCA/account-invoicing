# -*- coding: utf-8 -*-
# Copyright 2012 Associazione OpenERP Italia (<http://www.openerp-italia.org>).
# Copyright 2016 Davide Corio (Abstract)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        for invoice in self:
            inv_type = invoice.type
            if inv_type == 'out_invoice' or inv_type == 'out_refund':
                number = invoice.move_name
                date_invoice = invoice.date_invoice
                journal = invoice.journal_id.id
                records = self.search([
                    ('type', '=', inv_type),
                    ('date_invoice', '>', date_invoice),
                    ('number', '<', number),
                    ('journal_id', '=', journal)])
                if records:
                    raise ValidationError(
                        _('Cannot create invoice! Post the invoice with a\
                            greater date'))
        return res
