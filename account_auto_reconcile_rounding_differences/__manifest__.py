# -*- coding: utf-8 -*-
# Copyright 2019, Wolfgang Pichler, Callino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': "Auto reconcile rounding differences on payments",
    'author': 'Wolfgang Pichler (Callino),Odoo Community Association (OCA)',
    'summary': """
        Auto reconcile rounding differences on payments""",
    'category': 'Accounting',
    "website": "https://github.com/OCA/account-invoicing",
    'license': 'AGPL-3',
    'version': '10.0.1.0',
    'depends': ['account'],
    'data': [
        'views/res_config.xml',
    ],
}
