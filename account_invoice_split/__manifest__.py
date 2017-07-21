# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Account Invoice Split",
    'summary': """
        Split Quantity on invoice line""",
    'author': 'ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    'website': "https://www.acsone.eu",
    'category': 'Finance',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'wizard/account_invoice_split_view.xml',
    ],
}
