# -*- coding: utf-8 -*-
# Copyright 2012 Therp BV (<http://therp.nl>)
# Copyright 2013-2018 BCIM SPRL (<http://www.bcim.be>)

from odoo import models, fields, api


class AccountAccountType(models.Model):
    _inherit = 'account.account.type'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # Support xmlid in domain
        res = []
        if operator == '=':
            try:
                o = self.env.ref(name)
                if o._name == self._name:
                    res += o.name_get()
            except:
                pass
        if not res:
            res = super(AccountAccountType, self).name_search(
                name=name, args=args, operator=operator, limit=limit)
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_income = fields.Many2one(
        'account.account',
        string='Default Income Account',
        domain="[('user_type_id', '=', 'account.data_account_type_revenue')]",
        help='Default counterpart account for sales on invoice lines',
        company_dependent=True)
    auto_update_account_income = fields.Boolean(
        'Autosave Selection on Invoice Line',
        help='When an account is selected on an invoice line, '
             'automatically assign it as default income account',
        default=True)
    property_account_expense = fields.Many2one(
        'account.account',
        string='Default Expense Account',
        domain="[('user_type_id', '=', 'account.data_account_type_expenses')]",
        help='Default counterpart account for purchases on invoice lines',
        company_dependent=True)
    auto_update_account_expense = fields.Boolean(
        'Autosave Selection on Invoice Line',
        help='When an account is selected on an invoice line, '
             'automatically assign it as default expense account',
        default=True)
