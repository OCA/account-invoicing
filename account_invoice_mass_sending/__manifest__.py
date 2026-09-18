# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Mass Sending",
    "summary": """
        This addon adds a mass sending feature on invoices.""",
    "version": "15.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA), Open Net Sàrl",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        # ODOO
        "account",
        # OCA
        "queue_job",
    ],
    "data": [
        "data/queue_job.xml",
        "views/account_invoice_views.xml",
        "wizards/account_invoice_send.xml",
    ],
    "maintainers": ["jguenat"],
}
