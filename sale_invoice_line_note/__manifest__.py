# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Sale invoice line note",
    "summary": "Propagate sale order note lines to the invoice",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
    ],
    "data": [
        "wizard/sale_make_invoice_advance.xml",
    ],
}
