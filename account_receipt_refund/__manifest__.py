# Copyright 2020 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Refund Receipt",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "Allow to refund Receipts.",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing"
    "/tree/14.0/account_receipt_refund",
    "license": "AGPL-3",
    "depends": [
        "account",
        "account_receipt_base",
    ],
    "data": [
        "views/account_move_views.xml",
        "wizards/account_move_reversal_views.xml",
    ],
}
