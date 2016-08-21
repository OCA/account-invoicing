# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base UBL',
    'version': '8.0.1.0.0',
    'category': 'Hidden',
    'license': 'AGPL-3',
    'summary': 'Base module for Universal Business Language (UBL)',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': [
        'product_uom_unece',
        'account_tax_unece',
        ],
    'external_dependencies': {'python': ['PyPDF2']},
    'installable': True,
}
