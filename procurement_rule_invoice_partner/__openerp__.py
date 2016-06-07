# -*- coding: utf-8 -*-
# © 2016 KMEE - Luis Felipe Mileo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Stock Picking Route Partner Invoice",
    'version': '8.0.0.0.0',
    'category': 'Warehouse Management',
    'author': "KMEE,Odoo Community Association (OCA)",
    'website': 'http://www.kmee.com.br',
    'license': 'AGPL-3',
    'depends': [
        'stock_account',
        'procurement',
    ],
    'data': [
        'views/procurement_rule_view.xml',
    ],
    'installable': True
}
