# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Base Invoicing Mode",
    "version": "14.0.1.1.0",
    "summary": "Base module for handling multiple invoicing mode",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account", "queue_job", "sale"],
    "data": [
        "data/queue_job_data.xml",
        "views/res_partner.xml",
    ],
}
