# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Custom Rounding",
    "summary": "Custom taxes rounding method in invoices",
    "version": "15.0.1.0.0",
    "category": "Invoicing",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/partner_view.xml",
        "views/account_move_views.xml",
    ],
}
