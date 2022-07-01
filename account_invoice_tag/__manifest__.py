# Copyright 2022 Darío Cruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Tags",
    "summary": """Adds Tags to Account Invoice.""",
    "author": "Darío Cruz, Manuel Calero, Xtendoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Account Move",
    "version": "13.0.1.0.1",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "data/account_move_tag_data.xml",
        "security/ir.model.access.csv",
        "security/account_move_tag_security.xml",
        "views/account_move_tag.xml",
        "views/account_move.xml",
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["dariocruz"],
}
