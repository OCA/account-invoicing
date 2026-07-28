# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Invoice Transmit",
    "version": "16.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Invoice mass sending",
    "author": "BCIM, Odoo Community Association (OCA)",
    "maintainers": ["jbaudoux"],
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": [
        "account_invoice_transmit_method",
        "web_notify",
        "queue_job",
    ],
    "data": [
        "security/ir_model_access.xml",
        "views/account_move.xml",
        "views/account_invoice_print.xml",
        "wizards/account_invoice_transmit.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_functions.xml",
    ],
    "installable": True,
}
