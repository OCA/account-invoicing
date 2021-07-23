# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Acccount Move Original Partners",
    "version": "14.0.1.0.0",
    "summary": "Display original customers when creating invoices from"
    " multiple sale orders.",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account", "sale"],
    "data": ["views/account_move.xml"],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
