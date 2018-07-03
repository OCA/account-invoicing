# -*- coding: utf-8 -*-
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Partial Invoice',
    'version': '1.1',
    'category': 'Accounting & Finance',
    'summary': """Allow to partialy invoice Sale Order lines
    """,
    'author': "Camptocamp, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Ecosoft - Kitti U., "
              "Odoo Community Association (OCA)",
    'website': 'http://www.camptocamp.com',
    'license': 'AGPL-3',
    'depends': ['sale', 'account', 'sale_stock'],
    'data': [
        'view/sale_order_view.xml',
        'wizard/sale_view.xml',
    ],
    'test': [
        'test/partial_so_invoice.yml',
        'test/make_remaining_invoice.yml',
    ],
    'demo': [],
    'installable': True,
    'active': False,
}
