# -*- coding: utf-8 -*-
# Copyright 2016 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Stock invoices grouped by product',
    'summary':
    'Invoices created from picking grouped by product or by product category',
    'version': '8.0.1.0.0',
    'category': 'Generic Modules/Accounting',
    'author': "Agile Business Group, Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'stock_account',
        'stock_picking_invoice_link',
    ],
    'data': [
        'wizards/stock_invoice_onshipping_view.xml',
    ],
    'demo': [
        'demo/product.xml',
    ],
    'installable': True,
}
