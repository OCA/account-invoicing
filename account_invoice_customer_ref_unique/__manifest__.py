# Copyright 2023 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Unique Customer Invoice Number in Invoice",
    "version": "16.0.1.0.0",
    "summary": "Checks that customer invoices are not entered twice",
    "author": "Savoir-faire Linux, "
    "Acsone SA/NV, "
    "Open Source Integrators, "
    "Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account"],
    "data": ["views/account_move.xml"],
    "installable": True,
}
