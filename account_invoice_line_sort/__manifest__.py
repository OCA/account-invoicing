# Copyright 2015 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Sort Customer Invoice Lines",

    'summary': """
        Manage sort of customer invoice lines by customers""",

    'author': "Tecnativa, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/account-invoicing",

    'category': 'Finance',
    'version': '11.0.0.1.0',
    'license': 'AGPL-3',

    'depends': [
        'account',
    ],

    'data': [
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml'
    ],

    'demo': [
    ],
    'installable': True,
}
