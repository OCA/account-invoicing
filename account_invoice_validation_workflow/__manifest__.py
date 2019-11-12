# Author: Joël Grand-Guillaume (Camptocamp)
# Author: Dhara Solanki <dhara.solanki@initos.com>
# Copyright 2010-2015 Camptocamp SA
# Copyright initOS GmbH 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Add "To Send" and "To Validate" states in Invoices',
    'version': '11.0.1.0.0',
    'category': 'Generic Modules/Invoicing',
    'author': "initOS GmbH, Camptocamp, Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/account-invoicing',
    'license': 'AGPL-3',
    'depends': ['account_invoicing'],
    'data': [
        'views/invoice_view.xml',
    ],
    'installable': True,
}
