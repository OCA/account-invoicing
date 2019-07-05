# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Debit Notes',
    'summary': """
        Create debit note from invoice and vendor bill""",
    'version': '12.0.1.0.0',
    'website': 'https://github.com/OCA/account-invoicing',
    'author': 'Eocosft,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'wizard/account_invoice_debitnote_view.xml',
        'views/account_invoice_view.xml',
        'views/account_view.xml',
    ],
    'installable': True,
}
