# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2015 initOS GmbH (<http://www.initos.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Sale order line gross price subtotal',
    'summary': 'Show gross price in subtotal for for sale.order.line',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'website': 'http://www.initos.com, https://odoo-community.org',
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
