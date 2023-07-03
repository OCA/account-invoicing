# Copyright 2020-2023 Groupe Voltaire
# @author Guillaume MASSON <guillaume.masson@groupevoltaire.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Lot",
    "summary": "add and propagate lot number from sale to invoice line",
    "version": "16.0.1.0.0",
    "category": "CAT",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Akretion, Groupe Voltaire, Odoo Community Association (OCA)",
    "maintainers": ["metaminux", "Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "sale_order_lot_selection",
    ],
    "data": [
        "views/account_move.xml",
    ],
}
