# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Account Billing Summary",
    "summary": "Summarize billing revenue by period",
    "version": "18.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Accounting/Accounting",
    "depends": ["account"],
    "external_dependencies": {"python": ["openpyxl"]},
    "data": [
        "security/ir.model.access.csv",
        "wizard/billing_summary_wizard_view.xml",
        "views/menu_views.xml",
    ],
    "installable": True,
    "maintainers": ["ROBBYHOOD9"],
}
