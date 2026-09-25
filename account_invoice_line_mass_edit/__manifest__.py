# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Line Mass Edit",
    "version": "16.0.1.0.0",
    "summary": "Mass edit the lines of an invoice",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Accounting",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_move_line_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
    "maintainers": ["florian-dacosta"],
}
