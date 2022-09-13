# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Return Refund Option",
    "summary": "Update the refund options in pickings",
    "version": "15.0.1.0.1",
    "development_status": "Production/Stable",
    "category": "Sales",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock_account", "purchase_stock", "sale_stock"],
    "data": ["views/stock_picking_view.xml"],
    "maintainers": ["sergio-teruel"],
}
