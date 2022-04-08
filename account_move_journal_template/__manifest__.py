# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Move Journal Template",
    "summary": "Template for Journal Entries and Items, per product.",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "development_status": "Beta",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_journal_template.xml",
        "views/account_move_views.xml",
    ],
    "demo": ["demo/account_move_journal_template.xml"],
}
