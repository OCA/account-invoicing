# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Acccount Move Accounting Description",
    "version": "14.0.1.0.1",
    "summary": "Adds an 'accounting description' on products",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account", "product"],
    "data": [
        "views/product_template.xml",
        "views/account_move.xml",
        "reports/invoice.xml",
    ],
    "installable": True,
}
