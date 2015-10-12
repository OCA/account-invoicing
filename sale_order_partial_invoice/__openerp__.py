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
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Allow to partially invoice sale order lines
===========================================

With a sale order in 'manual' invoicing policy, when the user selects to
invoice some SO lines, a new wizard is display in which it is possible to
select how much of the different lines is to be invoiced. The amounts
invoiced and the amounts delivered are also displayed. When generating an
invoice for the whole sale order, the partial invoices are taken into
account and only the amounts not already invoiced are part of the new
invoice.

Credits
=======

Contributors
------------

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Kitti U. <kittiu@ecosoft.co.th>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
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
