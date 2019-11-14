# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sales order invoicing grouping criteria',
    'version': '11.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/sale_invoicing_grouping_criteria_views.xml',
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': ['pedrobaeza'],
}
