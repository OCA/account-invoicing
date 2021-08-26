# Copyright 2019 ACSONE SA/NV
# Copyright 2021 Julien Guenat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Mass Sending",
    "description": """
        This addon adds a mass sending feature on invoices.""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA),Julien Guenat",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        # ODOO
        "account",
        # OCA
        "queue_job",
        "web_notify",
    ],
    "data": [
        "views/account_invoice_views.xml",
        "wizard/mass_send_print.xml",
    ],
}
