# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Account invoice refund line",
    "version": "13.0.1.1.0",
    "category": "Accounting & Finance",
    "summary": "This module allows the user to refund specific lines in a invoice",
    "author": "Creu Blanca, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_move_line_views.xml",
        "wizards/account_move_reversal_view.xml",
    ],
    "installable": True,
}
