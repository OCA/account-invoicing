# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Line Warehouse",
    "summary": "Adds a warehouse field on invoice lines, computed "
    "from linked sale/purchase order lines.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale_stock",
        "purchase_stock",
    ],
    "data": [],
    "installable": True,
}
