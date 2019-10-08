# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Repair Link',
    'summary': "Adds a link in the invoice to the repair from which it "
               "was generated",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Eficent Business and IT Consulting Services S.L.,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'depends': [
        'account',
        'repair',
    ],
    'data': [
        'views/account_invoice_views.xml',
    ],
}
