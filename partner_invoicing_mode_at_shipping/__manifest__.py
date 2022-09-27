# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Partner Invoicing Mode At Shipping",
    "version": "15.0.1.0.0",
    "summary": "Create invoices automatically when goods are shipped.",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "data": [
        "data/queue_job_data.xml",
    ],
    "depends": ["account", "partner_invoicing_mode", "queue_job", "stock"],
}
