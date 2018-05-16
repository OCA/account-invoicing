# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Blocking',
    'summary': """
        This module allows the user to set a blocking (No Follow-up) flag on
        invoices.""",
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'author': 'Acsone SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'depends': ['account'],
    'data': [
        'views/account_invoice.xml',
    ],
}
