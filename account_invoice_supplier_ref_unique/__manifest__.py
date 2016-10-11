# -*- coding: utf-8 -*-
# Copyright 2016 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Unique Supplier Invoice Number in Invoice',
    'version': '9.0.1.0.0',
    'summary': 'Checks that supplier invoices are not entered twice',
    'author':
        "Savoir-faire Linux, Acsone SA/NV, Odoo Community Association (OCA)",
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'depends': [
        'account'
    ],
    'data': ['views/account_invoice.xml'],
}
