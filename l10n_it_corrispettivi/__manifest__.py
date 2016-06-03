# -*- coding: utf-8 -*-
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Italian Localization - Corrispettivi',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'Odoo Italian Community, Agile Business Group, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.odoo-italia.org',
    'license': 'AGPL-3',
    "depends": ['account'],
    "data": [
        'partner_data.xml',
        'account_view.xml',
        'installer_view.xml',
    ],
    "active": False,
    'installable': True
}
