# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Business Document Import',
    'version': '8.0.1.0.0',
    'category': 'Hidden',
    'license': 'AGPL-3',
    'summary': 'Provides technical tools to import sale orders or supplier '
    'invoices',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['product', 'base_vat_sanitized'],
    'external_dependencies': {'python': ['PyPDF2']},
    'installable': True,
}
