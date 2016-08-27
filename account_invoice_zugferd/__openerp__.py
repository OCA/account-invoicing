# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice ZUGFeRD',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Generate ZUGFeRD customer invoices',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['account_payment_partner', 'base_zugferd', 'base_vat'],
    'external_dependencies': {'python': ['PyPDF2', 'lxml']},
    'installable': True,
}
