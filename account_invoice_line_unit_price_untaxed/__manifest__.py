# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Line Unit Price Untaxed",
    "summary": """
        This module allows to display unit prices without taxes if prices
        are managed with included taxes""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_move_line.xml",
        "report/report_account_move.xml",
    ],
}
