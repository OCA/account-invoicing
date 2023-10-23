# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Website Hide Invoice",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": """Open Source Integrators,
        Serpent Consulting Services,
        Odoo Community Association (OCA)""",
    "summary": """Hide invoices on customer portal.""",
    "category": "Invoicing Management",
    "maintainers": ["Khalid-SerpentCS"],
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_portal_templates.xml",
    ],
    "installable": True,
}
