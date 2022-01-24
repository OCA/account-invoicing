# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Alternate Payer",
    "summary": "Set a alternate payor/payee in invoices",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Accounting",
    "author": "ForgeFlow S.L.,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
        "views/res_partner_view.xml",
    ],
}
