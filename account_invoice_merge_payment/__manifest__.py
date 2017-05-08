# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "account_invoice_merge_payment",
    'summary': """
        Use invoice merge regarding fields on Account Payment Partner""",
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://www.acsone.eu",
    'category': 'Invoicing & Payments',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_merge',
        'account_payment_partner',
    ],
    'auto_install': True,
    'installable': False,
}
