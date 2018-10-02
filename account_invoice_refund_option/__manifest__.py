# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Create Refund Invoice",
    "summary": "Allows you to create directly a refund without starting from "
               "an invoice",
    "version": "11.0.1.0.0",
    "category": "Accounting",
    "website": "https://www.tecnativa.com/",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
}
