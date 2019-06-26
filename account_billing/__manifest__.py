# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Billing Process',
    'summary': 'Group invoice as billing before payment',
    'version': '12.0.1.0.0',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/account-invoicing/',
    'category': 'Account',
    'depends': ['account'],
    'data': [
        'data/account_billing_sequence.xml',
        'data/account_invoice.xml',
        'security/ir.model.access.csv',
        'views/account_billing.xml',
        'views/account_invoice_view.xml',
        'report/report_billing.xml',
        'report/report.xml',
        ],
    'installable': True,
    'development_status': 'alpha',
    'maintainers': ['Saran440'],
}
