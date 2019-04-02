# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Mass Sending",
    "description": """
        This addon adds a mass sending feature on invoices.""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        # ODOO
        "account",
        # OCA
        "queue_job",
        "web_notify",
    ],
    "data": ["views/account_invoice_views.xml"],
}
