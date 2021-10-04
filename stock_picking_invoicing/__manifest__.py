# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Stock Picking Invoicing",
    'version': '12.0.2.1.0',
    'category': 'Warehouse Management',
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/account-invoicing',
    'license': 'AGPL-3',
    "depends": [
        "stock",
        "account",
        "stock_picking_invoice_link",
    ],
    "data": [
        "wizards/stock_invoice_onshipping_view.xml",
        "views/stock_move.xml",
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
    ],
    "demo": [
        "demo/stock_picking_demo.xml"
    ],
    'installable': True,
}
