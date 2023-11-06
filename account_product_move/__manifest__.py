# Copyright 2022-2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Product Move",
    "summary": "Extra journal entries and items, per product or category.",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "development_status": "Beta",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/account_product_move.xml",
        "views/product_category.xml",
        "views/product_template.xml",
        "views/ir_ui_menu.xml",
    ],
}
