# -*- coding: utf-8 -*-
# Copyright 2015 Alessio Gerace <alessio.gerace@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Unit rounded invoice by Currency',
    'version': '8.0.1.0.0',
    'category': 'Accounting',
    'author': "Agile Business Group, Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com/',
    'license': 'AGPL-3',
    'depends': ['account_invoice_rounding'],
    'data': [
        'views/res_config_view.xml',
        'security/ir.model.access.csv',
    ],
    "demo": ['demo/data.xml'],
    'installable': True,
    'auto_install': False,
    'application': False
}
