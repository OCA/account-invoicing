# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase: Auto Update Quantity on Draft Invoices",
    "summary": """Automatically updates draft vendor bill lines based on qty_to_invoice""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "maintainers": ["lmignon"],
    "installable": True,
    "depends": ["purchase_stock"],
    "data": [
        "views/account_move.xml",
        "views/res_config_settings.xml",
    ],
    "demo": [],
    "maturity": "alpha",
}
