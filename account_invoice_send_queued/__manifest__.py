# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Enqueue account invoice email sending",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account", "queue_job"],
    "data": [
        "data/queue_job.xml",
        "views/queue_job_views.xml",
        "views/account_invoice_views.xml",
        "wizards/account_invoice_send_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["sergio-teruel"],
}
