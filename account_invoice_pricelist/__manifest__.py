# -*- coding: utf-8 -*-
# © 2015-2016 GRAP <http://www.grap.coop>.
# © 2015-2017 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later <http://www.gnu.org/licenses/agpl.html>.
{
    'name': 'Account - Pricelist on Invoices',
    'version': '8.0.1.0.0',
    'summary': 'Add partner pricelist on invoices',
    'category': 'Accounting & Finance',
    'author': 'GRAP,Therp BV,Odoo Community Association (OCA)',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base_view_inheritance_extension',
        'account',
    ],
    'data': [
        'view/account_invoice_view.xml',
    ],
}
