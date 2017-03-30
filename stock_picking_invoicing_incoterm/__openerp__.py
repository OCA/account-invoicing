# -*- coding: utf-8 -*-
# Copyright 2014-2015 Agile Business Group sagl
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Stock Picking Invoicing Incoterm",
    'version': '8.0.1.0.0',
    'category': 'Warehouse Management',
    'author': "Agile Business Group, Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'sale_stock',
    ],
    'data': [
        'account_invoice_view.xml',
        'stock_view.xml',
    ],
    'test': [
        'test/stock_picking_invoicing_incoterm.yml',
    ],
    'installable': True
}
