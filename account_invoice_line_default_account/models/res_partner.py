# -*- coding: utf-8 -*-
# Copyright 2012 Therp BV (<http://therp.nl>)
# Copyright 2013-2018 BCIM SPRL (<http://www.bcim.be>)

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_income = fields.Many2one(
        'account.account',
        string='Default Income Account',
        domain='''[('user_type_id', '=', 'Income')]''',
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
        domain='''[('user_type_id', '=', 'Expenses')]''',
        help='Default counterpart account for purchases on invoice lines',
        company_dependent=True)
    auto_update_account_expense = fields.Boolean(
        'Autosave Selection on Invoice Line',
        help='When an account is selected on an invoice line, '
             'automatically assign it as default expense account',
        default=True)
