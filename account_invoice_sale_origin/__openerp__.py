# -*- coding: utf-8 -*-
# © 2010-2013 Savoir-faire Linux
# © 2015 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice Sale Origin',
    'version': '8.0.1.1.0',
    'category': 'Accounting & Finance',
    'author': "Savoir-faire Linux, Odoo Community Association (OCA)",
    'website': 'http://www.savoirfairelinux.com/',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'sale'
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}
