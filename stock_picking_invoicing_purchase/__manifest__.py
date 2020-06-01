# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Stock Picking Invoicing Purchase",
    'version': '12.0.2.0.0',
    'category': 'Warehouse Management',
    'author': "Sergio Corato, Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/account-invoicing',
    'license': 'AGPL-3',
    "depends": [
        "purchase",
        "purchase_discount",
        "stock_picking_invoicing",
    ],
    'installable': True,
    'auto_install': True,
}
