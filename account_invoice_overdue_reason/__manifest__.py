# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Overdue Reason",
    "summary": """Adds an overdue reason on customer invoices to classify and
    track overdue payments.""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "data": [
        "data/account_move_overdue_reason.xml",
        "security/account_move_overdue_reason.xml",
        "views/account_move_overdue_reason_views.xml",
        "views/account_move_views.xml",
    ],
    "maintainers": ["sbejaoui"],
}
