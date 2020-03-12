# Copyright 2020 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

{
    "name": "Account Invoice Secondary Unit",
    "summary": "Allows to use secondary unit in invoice lines.",
    "version": "13.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account", "product_secondary_unit"],
    "data": ["views/account_move_view.xml", "report/account_invoice_report.xml"],
}
