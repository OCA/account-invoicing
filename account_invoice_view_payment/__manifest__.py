# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#        (https://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Account Invoice View Payment",
    "summary": "Access to the payment from an invoice",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-payment",
    "author": "Eficent, " "Odoo Community Association (OCA)",
    "category": "Accounting",
    "depends": ["account"],
    "data": ["views/account_payment_view.xml", "views/account_move_view.xml"],
    "installable": True,
}
