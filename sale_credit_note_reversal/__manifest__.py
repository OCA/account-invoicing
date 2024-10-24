# Copyright 2024 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Sale Credit Note Reversal",
    "summary": """Allow to revert a credit note""",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_management"],
    "data": [
        "views/account_move_views.xml",
    ],
}
