# Copyright (C) 2024-Today - KMEE (<http://www.kmee.com.br>).
# @author Diego Paradeda <diego.paradeda@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Stock Create",
    "summary": """This addon creates stock transfers from an account move""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "stock",
        "account",
        "stock_picking_invoice_link",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Data
        # Views
        "views/account_move_views.xml",
        # Wizards
        "wizards/account_move_match_picking_views.xml",
    ],
    "demo": [],
    "development_status": "Alpha",
}
