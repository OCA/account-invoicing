# -*- coding: utf-8 -*-
# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Invoice - Change Currency',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Allows to change currency of Invoice by wizard',
    'author': 'Komit Consulting, Odoo Community Association (OCA)',
    'website': 'https://komit-consulting.com',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'wizard/wizard_change_invoice_currency.xml',
        'views/account_invoice.xml',
    ],
    "installable": True
}
