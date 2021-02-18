# Copyright 2021 Lorenzo Battistini @ TAKOBI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Payment term - date ranges",
    "summary": "Payment terms based on date ranges",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/payment_term_views.xml",
    ],
    "demo": [
        "demo/account_demo.xml",
    ],
    "excludes": [
        "account_payment_term_extension",  # due to its override of "compute"
    ],
}
