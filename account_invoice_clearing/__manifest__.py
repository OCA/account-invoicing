# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Account Invoice Clearing",
    "summary": "Account invoice clearing wizard",
    "version": "15.0.0.1.3",
    "development_status": "Alpha",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide"],
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_view.xml",
        "wizards/account_invoice_clearing_wizard_views.xml",
    ],
}
