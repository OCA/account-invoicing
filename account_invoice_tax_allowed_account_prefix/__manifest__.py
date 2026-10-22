# Copyright 2026 ACSONE SA/NV,BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Tax Allowed Account Prefix",
    "summary": """Restrict invoice taxes based on account code prefix""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,BCIM,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "data": ["views/account_tax.xml", "views/account_move.xml"],
    "demo": [],
    "maintainers": ["sbejaoui", "jbaudoux"],
}
