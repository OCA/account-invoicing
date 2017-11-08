# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
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
##############################################################################

{
    'name': 'Sale Partial Invoice',
    'version': '1.1',
    'category': 'Accounting & Finance',
    'summary': """Allow to partialy invoice Sale Order lines
    """,
    'author': "Camptocamp, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Ecosoft - Kitti U., "
              "Odoo Community Association (OCA)",
    'website': 'http://www.camptocamp.com',
    'license': 'AGPL-3',
    'depends': ['sale', 'account', 'sale_stock'],
    'data': [
        'view/sale_order_view.xml',
        'wizard/sale_view.xml',
    ],
    'test': [
        'test/partial_so_invoice.yml',
        'test/make_remaining_invoice.yml',
    ],
    'demo': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
