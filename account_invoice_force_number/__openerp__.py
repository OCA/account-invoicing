# -*- coding: utf-8 -*-
# Copyright 2011-2016 Agile Business Group
# Copyright 2017 Alex Comba - Agile Business Group
# Backort and testing on 9.0 by Piotr Cierkosz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Force Invoice Number',
    'version': '9.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Allows to force invoice numbering on specific invoices',
    'author': 'Piotr Cierkosz, Agile Business Group, Odoo Community Association (OCA)',
    'website': 'https://www.cier.tech',
    'license': 'AGPL-3',
    'depends': [
        'account'
    ],
    'data': [
        'security/security.xml',
        'views/account_invoice_view_customer.xml',
        'views/account_invoice_view_vendor.xml',
    ],
    'installable': True,
}
