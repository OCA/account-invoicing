# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Invoice Salesteam on Delivery Order',
    'version': '1.0',
    'category': 'Hidden',
    'description': """
This module allows:

* Invoices made from a delivery order to use the sale order sales team.
* Sale Order to get the partner's default sales team.

""",
    'author': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'images': [],
    'depends': [
        'sale_crm',
        'stock'
    ],
    'data': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
}
