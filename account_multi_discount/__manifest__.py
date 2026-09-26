# Copyright 2026 Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Account Multi Discount",
    "summary": "Apply unlimited multiplicative discounts on invoice lines "
    "through a distribution edited via a dedicated widget.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "maintainers": ["LorenzoC0"],
    "website": "https://github.com/OCA/account-invoicing",
    "license": "LGPL-3",
    "depends": [
        "account",
    ],
    "excludes": [
        "account_invoice_triple_discount",
    ],
    "data": [
        "views/account_move_views.xml",
        "report/account_invoice_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_multi_discount/static/src/components/**/*",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
