# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Merge Stock',
    'summary': """
        Glue module between account invoice merge and
        stock picking invoice link""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'http://acsone.eu',
    'depends': [
        'stock_picking_invoice_link',
        'account_invoice_merge',
    ],
    'auto_install': True,
}
