# Copyright 2026 Swanand Beedkar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Partner Email Recipients",
    "summary": "Pre-fills customer's invoice recipients on send wizards.",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "Swanand Beedkar, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "maintainers": ["swanandbidkar108-oss"],
    "development_status": "Beta",
    "depends": ["account"],
    "data": [
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
}
