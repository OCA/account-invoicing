# -*- coding: utf-8 -*-
# Copyright 2014-2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_analytic_accounts(self):
        for invoice in self:
            invoice.account_analytic_ids =\
                invoice.mapped('invoice_line_ids.account_analytic_id.id')

    @api.multi
    def _search_analytic_accounts(self, operator, value):
        invoice_line_obj = self.env['account.invoice.line']
        invoice_line_ids = invoice_line_obj.search(
            [('account_analytic_id', operator, value)])
        invoice_id = self.search([('invoice_line_ids', 'in',
                                   invoice_line_ids.ids)])
        if invoice_id:
            return [('id', 'in', tuple(invoice_id.ids))]
        else:
            return []

    account_analytic_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        compute='_compute_analytic_accounts',
        search='_search_analytic_accounts',
        string='Analytic Account',
        readonly=True
    )
