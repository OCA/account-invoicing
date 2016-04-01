# -*- coding: utf-8 -*-
# © 2016 <OCA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Stock Picking Invoicing",
    'version': '9.0.1.0.0',
    'category': 'Warehouse Management',
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": [
        "stock",
        "account"
        
        ],
    "data": [
        "wizard/stock_invoice_onshipping_view.xml",
        "views/stock_view.xml",
    ],
    
    'installable': True
}
