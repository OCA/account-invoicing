# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Alternate Payer',
    'summary': 'Set a alternate payor/payee in invoices',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'author': 'Eficent,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing/',
    'depends': ['account'],
    'data': [
        'views/account_invoice_views.xml',
    ],
}
