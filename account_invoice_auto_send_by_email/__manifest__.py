# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Account Invoice Auto Send By Email",
    "summary": "Invoice with the email transmit method are send automatically.",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["account", "account_invoice_transmit_method", "queue_job"],
    "website": "https://github.com/OCA/account-invoicing",
    "data": [
        "data/ir_cron.xml",
    ],
    "installable": True,
}
