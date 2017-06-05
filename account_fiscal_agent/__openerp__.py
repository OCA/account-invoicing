# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Fiscal Agent',
    'version': '8.0.1.0.0',
    'category': 'Account',
    'summary': 'Account Fiscal Agent',
    'website': 'https://www.serpentcs.com',
    'author': "Serpent Consulting Services Pvt. Ltd., "
              "Agile Business Group, "
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_position.xml'
    ],
    'installable': True,
    'auto_install': False
}
