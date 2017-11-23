# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Timesheet details invoice',
    'summary': 'Add timesheet details in invoice line',
    'version': '11.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.tecnativa.com',
    'depends': [
        'sale_timesheet',
    ],
    'data': [
        'views/sale_view.xml',
        'views/res_config_view.xml',
    ],
    'installable': True,
}
