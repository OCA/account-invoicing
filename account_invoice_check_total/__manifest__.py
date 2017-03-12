# -*- coding: utf-8 -*-
# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Check Total',
    'summary': """
        Check if the verification total is equal to the bill's total""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Acsone SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu/',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_config_settings.xml',
        'security/account_invoice_security.xml',
        'views/account_invoice.xml',
    ],
}
