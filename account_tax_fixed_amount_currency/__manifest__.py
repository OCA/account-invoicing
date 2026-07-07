# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Tax Fixed Amount Currency",
    "summary": "Allow fixed-amount taxes to have their amount expressed in a "
    "specific currency, with automatic conversion to the document currency.",
    "version": "19.0.1.0.0",
    "author": "Odoo Community Association (OCA), Camptocamp",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "development_status": "Alpha",
    "category": "Accounting/Accounting",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_tax_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_tax_fixed_amount_currency/static/src/helpers/account_tax.esm.js",
        ],
        "web.assets_frontend": [
            "account_tax_fixed_amount_currency/static/src/helpers/account_tax.esm.js",
        ],
    },
}
