# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Receipt Status",
    "summary": """Track reception progress on your invoices""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["purchase_line_receipt_status"],
    "data": [
        "views/account_move_line.xml",
        "views/account_move.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}
