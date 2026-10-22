# Copyright 2026
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Move Email Traceability",
    "summary": "Traces incoming emails to journal aliases that arrive without "
    "a valid PDF/XML attachment, so those vendor bills are not lost.",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["shirashi3771"],
    "license": "AGPL-3",
    "development_status": "Beta",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
