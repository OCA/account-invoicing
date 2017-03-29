# -*- coding: utf-8 -*-
# Copyright 2014-2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_analytic_accounts(self):
        for invoice in self:
            invoice.account_analytic_ids =\
            invoice.mapped('invoice_line_ids.account_analytic_id.id')

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_analytic_account_partner_ids(self):
        for invoice in self:
            invoice.account_analytic_partner_ids =\
            invoice.\
                mapped('invoice_line_ids.account_analytic_partner_id.id')

    @api.multi
    def _search_analytic_accounts(self, operator, value):
        invoice_line_obj = self.env['account.invoice.line']
        invoice_line_ids = invoice_line_obj.search(
            [('account_analytic_id', operator, value)])
        res = [('id', 'in', invoice_line_ids.ids)]
        return res or []

    @api.multi
    def _search_analytic_account_partner_ids(self, operator, value):
        invoice_line_obj = self.env['account.invoice.line']
        invoice_line_ids = invoice_line_obj.search(
            [('account_analytic_partner_id', operator, value)])
        res = [('id', 'in', invoice_line_ids.ids)]
        return res or []

    account_analytic_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        compute='_compute_analytic_accounts',
        search='_search_analytic_accounts',
        string='Analytic Account',
        readonly=True
        )
    account_analytic_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        compute='_compute_analytic_account_partner_ids',
        search='_search_analytic_account_partner_ids',
        string='Project Manager',
        readonly=True
        )
