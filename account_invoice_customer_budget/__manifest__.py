# Copyright 2023 Akretion
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Account Customer budget",
    "version": "16.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "This module allows the user to manage Customer Budget",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_invoice_view.xml",
        "views/account_journal_view.xml",
    ],
    "installable": True,
}
