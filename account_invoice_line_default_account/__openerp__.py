# -*- coding: utf-8 -*-
# Copyright 2012 Therp BV (<http://therp.nl>)
# Copyright 2013-2018 BCIM SPRL (<http://www.bcim.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Invoice Line Default Account',
    'version': '8.0.1.0.0',
    'depends': [
        'account'
    ],
    'author': 'Therp BV,BCIM,Odoo Community Association (OCA)',
    'contributors': ['Jacques-Etienne Baudoux <je@bcim.be>'],
    'license': 'AGPL-3',
    'category': 'Accounting',
    'data': [
        'views/res_partner.xml',
        'views/account_invoice.xml',
    ],
    'installable': True,
}
