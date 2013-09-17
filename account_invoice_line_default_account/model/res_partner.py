# -*- coding: UTF-8 -*-
'''
Created on 30 jan. 2013

@author: Ronald Portier, Therp

rportier@therp.nl
http://www.therp.nl
'''
from openerp.osv import orm
from openerp.osv import fields


class res_partner(orm.Model):
    _inherit = 'res.partner'
    
    _columns = {
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
            'Autosave account selected on invoice line',
            help='When an account is selected on an invoice line, automatically assign it as default expense account'),
    }
    
    _defaults = {
        'auto_update_account_expense': True,
    }
