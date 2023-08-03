# Copyright 2023 Tecnativa - Stefan Ungureanu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice CRM Tag",
    "version": "15.0.1.0.2",
    "category": "Accounting",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "views/account_invoice_views.xml",
        "report/account_invoice_report.xml",
    ],
    "application": False,
    "installable": True,
}
