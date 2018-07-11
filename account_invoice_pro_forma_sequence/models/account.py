# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    pro_forma_number = fields.Char(
        string='Pro-forma number', readonly=True, copy=False)

    @api.multi
    def action_invoice_proforma2(self):
        res = super(AccountInvoice, self).action_invoice_proforma2()
        today = fields.Date.today()
        for invoice in self:
            company = invoice.company_id
            if company.pro_forma_sequence:
                date = invoice.date_invoice or today
                sequence = company.pro_forma_sequence
                invoice.pro_forma_number = \
                    sequence.with_context(ir_sequence_date=date).next_by_id()
        return res
