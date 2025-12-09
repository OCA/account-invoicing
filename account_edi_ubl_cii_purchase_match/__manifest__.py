# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Edi Ubl Cii Purchase Match",
    "summary": """Extend UBL vendor bill import to automatically match and link bill
    lines to purchase order lines using the OrderReference and product label.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account_edi_ubl_cii", "purchase"],
    "data": [
        "security/account_move_line_select_purchase_line_wizard.xml",
        "wizards/account_move_line_select_purchase_line_wizard.xml",
        "views/account_move.xml",
        "views/purchase_order_line.xml",
    ],
    "demo": [],
}
