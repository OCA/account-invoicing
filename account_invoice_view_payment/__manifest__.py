# Copyright 2017 ForgeFlow S.L.
#        (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Account Invoice View Payment",
    "summary": "Access to the payment from an invoice",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "category": "Accounting",
    "depends": ["account"],
    "data": ["views/account_payment_view.xml", "views/account_move_view.xml"],
    "installable": True,
}
