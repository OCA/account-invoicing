# -*- coding: UTF-8 -*-
'''
Created on 30 jan. 2013

@author: Ronald Portier, Therp
@contributor: Jacques-Etienne Baudoux, BCIM
'''

from openerp.osv import orm
from openerp.osv import fields


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'property_account_income': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string='Default Income Account',
            view_load=True,
            domain='''[('user_type.report_type', '=', 'income')]''',
            help='Default counterpart account for sales on invoice lines',
            required=False),
        'auto_update_account_income': fields.boolean(
            'Autosave Selection on Invoice Line',
            help='When an account is selected on an invoice line, '
                 'automatically assign it as default income account'),
        'property_account_expense': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string='Default Expense Account',
            view_load=True,
            domain='''[('user_type.report_type', '=', 'expense')]''',
            help='Default counterpart account for purchases on invoice lines',
            required=False),
        'auto_update_account_expense': fields.boolean(
            'Autosave Selection on Invoice Line',
            help='When an account is selected on an invoice line, '
                 'automatically assign it as default expense account'),
    }

    _defaults = {
        'auto_update_account_income': True,
        'auto_update_account_expense': True,
    }
