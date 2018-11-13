# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Date Required',
    'summary': """
        Requires invoice date before validation to avoid Odoo setting 'today'
        as default if not filled in.""",
    'version': '10.0.1.0.0',
    'development_status': 'Alpha',
    'maintainers': ['rousseldenis'],
    'category': 'Accounting',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'depends': [
        'account',
    ],
}
