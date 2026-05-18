# Copyright 2023 Simone Rubino - TAKOBI
# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base for Receipt Management",
    "summary": "Base fields and methods for better Receipts Management.",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "TAKOBI, Francesco Ballerini, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_fiscal_position_views.xml",
        "views/res_partner_views.xml",
        "reports/account_invoice_report_views.xml",
    ],
}
