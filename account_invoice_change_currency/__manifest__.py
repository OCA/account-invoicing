# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Invoice - Change Currency',
    'version': '11.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Allows to change currency of Invoice by wizard',
    'author': 'Komit Consulting, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'data/ir_server_actions.xml',
        'data/message_subtype.xml',
        'views/account_invoice.xml',
    ],
    "installable": True
}
