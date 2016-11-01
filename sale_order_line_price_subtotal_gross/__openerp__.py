# -*- coding: utf-8 -*-
# © 2015 initOS GmbH (<http://www.initos.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale order line gross price subtotal',
    'summary': 'Show gross price in subtotal for for sale.order.line',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'website': 'https://odoo-community.org',
    'author': 'initOS GmbH, Odoo Community Association (OCA)',
    "license": "AGPL-3",
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'sale',
    ],
    'data': [
        'sale_view.xml',
    ],
}
