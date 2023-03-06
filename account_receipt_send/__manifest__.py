# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Receipts Print and Send",
    "summary": "Send receipts",
    "version": "15.0.1.0.1",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide"],
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_move_views.xml",
        "data/mail_template_data.xml",
    ],
}
