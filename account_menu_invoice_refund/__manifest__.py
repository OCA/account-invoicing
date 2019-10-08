# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Accunt Menu - Invoice & Refund',
    'version': '12.0.1.0.0',
    'summary': 'New invoice menu that combine invoices and refunds',
    'category': 'Accounting & Finance',
    'author': 'Ecosoft, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/account-invoicing/',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'development_status': 'beta',
    'maintainers': ['kittiu'],
    'post_load': 'post_load_hook',
}
