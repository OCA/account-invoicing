# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "Account Invoice View Payment",
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'summary': "Access to the payment from an invoice",
    'author': 'Eficent,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-payment',
    'license': 'AGPL-3',
    "depends": [
        'account',
    ],
    "data": [
        'views/account_payment_view.xml',
        'views/account_invoice_view.xml',
    ],
    "installable": True
}
