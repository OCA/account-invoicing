# Copyright 2020 Le Filament
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Confirm Popup",
    "summary": "Adds a confirmation popup before validation",
    "version": "12.0.1.0.0",
    "author": "Le Filament, Odoo Community Association (OCA)",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "demo": [],
    'data': [
        'views/account_invoice_view.xml',
    ],
    "installable": True,
    "auto_install": False,
}
