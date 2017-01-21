# -*- coding: utf-8 -*-
# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Account Invoice Merge Purchase",

    'summary': """Compatibility between purchase and account invoice merge""",
    'author': "ACSONE SA/NV,Noviat,Odoo Community Association (OCA)",
    'website': "http://acsone.eu",
    'category': 'Finance',
    'version': '8.0.2.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_merge',
        'purchase',
    ],
    'auto_install': True,
    'installable': False,
}
