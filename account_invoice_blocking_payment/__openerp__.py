# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Blocking Payment',
    'summary': """
        This module deactivates the payment button of a blocked invoice.""",
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'www.acsone.eu',
    'depends': [
        'account_payment_order',
        'account_invoice_blocking',
    ],
    'data': [
        'views/account_invoice.xml',
    ],
    'auto_install': True,
}
