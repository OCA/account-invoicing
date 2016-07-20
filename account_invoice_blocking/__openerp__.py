# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Blocking',
    'summary': """
        This module allows the user to set a blocking (No Follow-up)
        flag directly on the invoice. This facilitates the blocking of
        the invoice's move lines.""",
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'author': 'Acsone SA/NV,Odoo Community Association (OCA)',
    'website': 'www.acsone.eu',
    'depends': ['account'],
    'data': [
        'views/account_invoice.xml',
    ],
    'demo': [
    ],
}
