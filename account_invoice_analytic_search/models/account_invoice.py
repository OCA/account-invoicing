# -*- coding: utf-8 -*-
# Copyright 2014-2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from openerp import fields, models, api


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.depends('invoice_line_ids')
    def _get_analytic_accounts(self):
        res = {}
        for invoice in self:
            for invoice_line in invoice.invoice_line_ids:
                if invoice_line and invoice_line.account_analytic_id:
                    res[invoice.id].append(invoice_line.account_analytic_id.id)
        return res

    @api.depends('invoice_line_ids')
    def _get_analytic_account_user_ids(self):
        res = {}
        for invoice in self:
            res[invoice.id] = []
            for invoice_line in invoice.invoice_line_ids:
                if invoice_line.account_analytic_id and\
                        invoice_line.account_analytic_id.user_id:
                    res[invoice.id].append(
                        invoice_line.account_analytic_id.user_id
                        )
        return res

    @api.multi
    def _search_analytic_accounts(self, operator, value):
        invoice_line_obj = self.env['account.invoice.line']
        invoice_line_ids = invoice_line_obj.search(
                [('account_analytic_id', operator, value)])
        res = [('id', 'in', invoice_line_ids.ids)]
        return res or []

    @api.multi
    def _search_analytic_account_user_ids(self, operator, value):
        invoice_line_obj = self.env['account.invoice.line']
        invoice_line_ids = invoice_line_obj.search(
                [('account_analytic_user_id', operator, value)])
        res = [('id', 'in', invoice_line_ids.ids)]
        return res or []

    account_analytic_ids = fields.Many2many(
        comodel_name='account.invoice.line',
        compute='_get_analytic_accounts',
        search='_search_analytic_accounts',
        string='Analytic Account',
        readonly=True
        )
    account_analytic_user_ids = fields.Many2many(
        comodel_name='res.users',
        compute='_get_analytic_account_user_ids',
        search='_search_analytic_account_user_ids',
        string='Project Manager',
        readonly=True
        )
