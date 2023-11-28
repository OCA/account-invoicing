# Copyright 2022 manaTec GmbH
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Mode Daily",
    "version": "14.0.1.0.0",
    "summary": "Create invoices automatically on a daily basis.",
    "author": "MT Software, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": [
        "account_invoice_base_invoicing_mode",
    ],
    "data": [
        "data/ir_cron.xml",
        "data/queue_job_data.xml",
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["mt-software-de"],
}
