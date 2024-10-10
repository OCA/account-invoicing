# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Purchase Quantity",
    "summary": """
        This module allows to display on purchase invoice lines the received
        and ordered quantities""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "purchase_stock",
    ],
    "data": ["views/account_move.xml"],
}
