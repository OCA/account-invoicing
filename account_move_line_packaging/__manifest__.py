# Copyright 2026 ACSONE SA/NV
# Copyright 2026 BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Line Packaging",
    "summary": """Add packaging to invoice lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, BCIM,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "data": ["views/account_move.xml"],
    "demo": [],
    "maintainers": ["jbaudoux", "sbejaoui"],
    "pre_init_hook": "pre_init_hook",
}
