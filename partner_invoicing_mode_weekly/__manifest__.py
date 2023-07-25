# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Mode Weekly",
    "version": "16.0.1.0.0",
    "summary": "Create invoices automatically on a weekly basis.",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": [
        "account",
        "partner_invoicing_mode",
        "queue_job",
        "sale",
    ],
    "data": [
        "data/ir_cron.xml",
        "data/queue_job_data.xml",
        "views/res_config_settings_views.xml",
    ],
}
