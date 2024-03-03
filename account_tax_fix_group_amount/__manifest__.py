#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Fix account tax grouped amount',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Fix grouped account tax amount',
    'website': 'https://github.com/OCA/account-invoicing',
    'author': 'TAKOBI,'
              'Odoo Community Association (OCA)',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_tax_views.xml',
    ],
}
