# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Global Discount Amount",
    "summary": "Allows to apply an amount of global discount in invoices.",
    "version": "14.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "data/product_data.xml",
        "views/account_move.xml",
    ],
    "installable": True,
}
