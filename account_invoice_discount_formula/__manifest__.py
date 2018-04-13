# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Account Invoice Discount Formula",
    'summary': "Express discounts on Invoice lines as mathematical formula",
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'http://www.onestein.eu',
    'category': 'Invoicing Management',
    'license': 'AGPL-3',
    'version': '11.0.1.0.0',
    'depends': [
        'account'
    ],
    'data': [
        'views/account_invoice_view.xml',
    ]
}
