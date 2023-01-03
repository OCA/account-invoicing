# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Account Invoice Payment Block",
    "version": "15.0.1.0.0",
    "summary": "Module to block payment of invoices",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account"],
    "data": [
        "views/account_move.xml",
    ],
    "application": False,
    "installable": True,
}
