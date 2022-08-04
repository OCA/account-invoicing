# Copyright 2021 Camptocamp
# Copyright 2022 manaTec GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Mode daily",
    "version": "14.0.1.0.0",
    "summary": "Create invoices automatically on a daily basis.",
    "author": "Camptocamp, Odoo Community Association (OCA), manatec GmbH",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": [
        "account",
        "account_invoice_base_invoicing_mode",
        "queue_job",
        "sale",
        "stock",  # For unit tests
    ],
    "data": [
        "data/ir_cron.xml",
        "data/queue_job_data.xml",
        "views/res_config_settings_views.xml",
    ],
}
