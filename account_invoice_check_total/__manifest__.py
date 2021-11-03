# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Check Total",
    "summary": """
        Check if the verification total is equal to the bill's total""",
    "version": "14.0.1.0.1",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Acsone SA/NV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/account_invoice_security.xml",
        "views/res_config_settings.xml",
        "views/account_invoice.xml",
    ],
}
