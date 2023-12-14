# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Account Invoice Discount Date",
    "summary": "Set the early discount date on invoices",
    "version": "15.0.1.0.1",
    "development_status": "Alpha",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_move_line_view.xml",
        "views/account_move_view.xml",
    ],
}
