# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account - Pricelist on Invoices',
    'version': '9.0.1.0.0',
    'summary': 'Add partner pricelist on invoices',
    'category': 'Accounting & Finance',
    'author': 'GRAP,'
              'Therp BV,'
              'Tecnativa,'
              'Odoo Community Association (OCA)',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'view/view.xml',
    ],
    'demo': [
        'demo/res_groups.yml',
    ],
    'installable': True,
}
