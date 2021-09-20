# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Restrict Invoice created from SO",
    "summary": "Restricts editing the Product, Quantity and Unit Price "
    "columns for invoice lines that originated in Sales Orders.",
    "version": "14.0.1.0.1",
    "category": "Accounting",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["sale_management"],
    "data": [
        "views/account_move.xml",
    ],
    "installable": True,
    "maintainer": "dreispt",
}
