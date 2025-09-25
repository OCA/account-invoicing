# Copyright 2021 Lorenzo Battistini @ TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Pro forma sequence for invoices",
    "summary": "Allow to use a different sequence for pro-forma invoices, "
    "with a specific PDF report",
    "version": "16.0.1.0.0",
    "category": "Invoicing Management",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "TAKOBI, Innovyou, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
        "report/report_proforma.xml",
    ],
    "auto_install": False,
    "post_init_hook": "assign_proforma_sequences",
}
