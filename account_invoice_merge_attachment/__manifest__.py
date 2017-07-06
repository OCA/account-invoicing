# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Merge Attachment',
    'summary': """
        Consider attachment during invoice merge process""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': 'https://www.acsone.eu',
    'depends': [
        'account_invoice_merge',
        'document',
    ],
    'data': [
        'wizards/invoice_merge.xml',
    ],
    'auto_install': True,
}
