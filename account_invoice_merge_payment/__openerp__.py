# -*- coding: utf-8 -*-
# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright (c) 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "account_invoice_merge_payment",
    'summary': """
        Use invoice merge regarding fields on Account Payment Partner""",
    'author': "ACSONE SA/NV, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': "http://acsone.eu",
    'category': 'Invoicing & Payments',
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_merge',
        'account_payment_partner',
    ],
    'installable': True,
}
