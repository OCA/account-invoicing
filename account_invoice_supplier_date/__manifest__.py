# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Supplier Invoice Date in header',
    'version': '12.0.1.0.0',
    'summary': 'Move accounting date in supplier invoice near date invoice',
    'author': 'Sergio Corato, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'depends': [
        'account',
    ],
    'data': [
        'views/account.xml',
    ],
    'installable': True,
}
