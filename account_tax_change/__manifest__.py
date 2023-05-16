# Copyright 2023 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Account Tax Change",
    "version": "16.0.1.0.1",
    "summary": "Configure your tax changes starting from a date.",
    "category": "Accounting & Finance",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_tax_change.xml",
        "wizards/account_move_apply_tax_change.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["sebalix"],
}
