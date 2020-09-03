# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Fix invoice tax rounding',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Fix invoice tax rounding globally',
    'website': 'https://github.com/OCA/account-invoicing',
    'author': 'Sergio Corato,'
              'Odoo Community Association (OCA)',
    'depends': [
        'account',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
