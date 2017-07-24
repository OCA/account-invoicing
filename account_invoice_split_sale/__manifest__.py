# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Account Invoice Split Sale",
    'summary': """
        Provide a compatibility between sale workflow and
        Account Invoice Split""",
    'author': 'ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    'website': "https://www.acsone.eu",
    'category': 'Finance',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_split',
        'sale',
    ],
    'auto_install': True,
}
