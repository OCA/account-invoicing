# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Import',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Import supplier invoices/refunds as PDF or XML files',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['account', 'base_iban', 'base_business_document_import'],
    'data': [
        'security/ir.model.access.csv',
        'security/rule.xml',
        'account_invoice_import_config_view.xml',
        'wizard/account_invoice_import_view.xml',
        'views/account_invoice.xml',
        'partner_view.xml',
    ],
    'images': ['images/sshot-wizard1.png'],
    'installable': True,
}
