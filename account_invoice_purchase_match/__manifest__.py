# Copyright 2026 OSS Factory
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Account Invoice Purchase Match",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "summary": "Match vendor bill lines with purchase order lines "
    "from a dedicated screen",
    "author": "Odoo SA, OSS Factory, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "LGPL-3",
    "development_status": "Beta",
    "depends": ["account", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/bill_to_po_wizard_views.xml",
        "views/purchase_bill_line_match_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
}
