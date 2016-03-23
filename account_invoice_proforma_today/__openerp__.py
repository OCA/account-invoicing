# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Proforma Today',
    'version': '7.0.1.0.0',
    'author': 'initOS GmbH, Odoo Community Association (OCA)',
    'category': '',
    'description':
    """
    The module extends the account.invoice model
    to set the date of the invoice as the today's
    date when changing state from 'proforma' to 'open'.
    """,
    'website': 'http://www.initos.com',
    'license': 'AGPL-3',
    'images': [],
    'depends': ['account',
                ],
    'data': [
    ],
    'active': False,
    'installable': True
}
