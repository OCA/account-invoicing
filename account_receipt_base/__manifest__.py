# Copyright 2020 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base for Receipt Management",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "Base fields and methods for better Receipts Management.",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing"
    "/tree/14.0/account_receipt_base",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_fiscal_position_views.xml",
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
        "reports/account_invoice_report_views.xml",
    ],
}
