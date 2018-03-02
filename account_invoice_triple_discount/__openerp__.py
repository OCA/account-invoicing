# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Invoice Triple Discount',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://tecnativa.com',
    'license': 'AGPL-3',
    'summary': 'Manage triple discount on invoice lines',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/account_tax.xml',
        'demo/account_invoice.xml',
    ],
    'installable': True,
}
