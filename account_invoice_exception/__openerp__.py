# -*- coding: utf-8 -*-
# © 2016 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice Exception',
    'summary': 'Custom exceptions on account invoice',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['invoice'],
    'data': [
        'account_invoice_workflow.xml',
        'views/account_invoice_view.xml',
        'data/account_invoice_exception_data.xml',
        'wizard/account_invoice_exception_confirm_view.xml',
        'security/ir.model.access.csv',
        'settings/account.invoice.exception.csv'
    ],
    'images': [],
    'installable': True
}
