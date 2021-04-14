# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Account Invoice Refund Sale Update',
    'version': '12.0.1.0.0',
    'summary': 'Add ability to update sale order when creating refund invoices.',
    'category': 'Accounting',
    'author': 'Sergio Corato - Efatto.it, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'maintainers': ['sergiocorato'],
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_refund_link',
        'sale_stock',
    ],
    'data': [
        'wizard/account_invoice_refund_view.xml',
    ],
    'installable': True,
}
