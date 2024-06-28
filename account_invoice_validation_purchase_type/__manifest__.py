# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Validation Purchase Type",
    "summary": "Account Invoice Validation Purchase Type",
    "version": "16.0.1.0.0",
    "depends": [
        "account_invoice_validation",
        "product",
    ],
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "data": [
        "views/account_move.xml",
        "views/product_template.xml",
    ],
    "demo": [
        "demo/product_product.xml",
    ],
    "installable": True,
}
