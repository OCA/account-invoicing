# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock account move reset to draft",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "version": "16.0.1.0.0",
    # Real dependency is stock_account but we need purchase_stock in tests
    "depends": ["purchase_stock"],
    "license": "AGPL-3",
    "category": "Warehouse Management",
    "installable": True,
    "maintainers": ["victoralmau"],
}
