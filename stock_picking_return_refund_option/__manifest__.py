# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Picking Return Refund Option',
    'summary': 'Update the refund options in pickings',
    'version': '12.0.1.0.0',
    'development_status': 'Production/Stable',
    'category': 'Sales',
    'website': 'https://github.com/OCA/account-invoicing',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock_account',
    ],
    'data': [
        'views/stock_picking_view.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'maintainers': ['sergio-teruel'],
}
