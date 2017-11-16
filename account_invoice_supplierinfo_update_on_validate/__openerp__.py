# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice - Supplier Info Update on Validate',
    'summary': 'In the supplier invoice, to validation proposes to update '
               'all products whose unit price on the line is different from '
               'the supplier price',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'website': 'http://akretion.com',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_supplierinfo_update',
    ],
    'installable': True,
    'data': [
        'views/account_invoice_view.xml',
        'wizard/wizard_update_invoice_supplierinfo.xml'
    ],
    'demo': [
        'demo/account_invoice.xml',
    ],
}
