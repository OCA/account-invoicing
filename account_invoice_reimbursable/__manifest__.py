# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Reimbursables management',
    'version': '12.0.1.0.0',
    'summary': 'Create the option to add reimbursables on invoices',
    'author': "Creu Blanca, Odoo Community Association (OCA)",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/report_invoice.xml',
    ],
    'installable': True,
}
