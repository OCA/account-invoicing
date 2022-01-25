# Copyright 2019-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Enqueue account invoice validation",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account", "queue_job"],
    "data": [
        "data/queue_job.xml",
        "views/queue_job_views.xml",
        "views/account_invoice_views.xml",
        "wizards/validate_account_move_view.xml",
    ],
    "installable": True,
    "development_status": "Production/Stable",
    "maintainers": ["pedrobaeza"],
}
