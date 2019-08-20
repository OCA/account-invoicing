# Copyright 2019 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Invoice Approval',
    'summary': 'Allows you to define who and when somebody '
               'has to approve an invoice.',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'category': 'Accounting & Finance',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'mail'
    ],
    'data': [
        'data/mail_template_data.xml',
        'data/mail_message_subtype_data.xml',

        'security/ir.model.access.csv',
        'security/security.xml',

        'views/account_invoice_view.xml',
        'views/account_invoice_approval_flow_view.xml',
        'menuitems.xml'
    ]
}
