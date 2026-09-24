# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Partner Invoicing Mail Subject",
    "summary": "Allows individual invoice subject line per partner.",
    "version": "19.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "NICO-SOLUTIONS, Odoo Community Association (OCA)",
    "maintainers": ["NICO-SOLUTIONS"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "depends": ["mail", "account"],
    "data": [
        "views/res_partner_views.xml",
    ],
}
