# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Line Mass Edit Start End Date",
    "version": "18.0.1.0.0",
    "summary": "Mass edit the start and end date one invoice lines",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Accounting",
    "license": "AGPL-3",
    "depends": ["account_invoice_line_mass_edit", "account_invoice_start_end_dates"],
    "data": [
        "views/account_move_line_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
    "maintainers": ["florian-dacosta"],
}
