# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Account Invoice Partner Company Only",
    "summary": "Restrict partner selection on invoices to companies only",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "OpenStudio SAS, Odoo Community Association (OCA)",
    "maintainers": ["maisim"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base_view_inheritance_extension",
        "account",
    ],
    "data": [
        "views/account_move_views.xml",
    ],
}
