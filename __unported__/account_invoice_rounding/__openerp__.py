# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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
{'name': 'Unit rounded invoice',
 'version': '1.0',
 'category': 'Accounting',
 'description': """
Unit rounded invoice (_`Swedish rounding`)
==========================================

Add a parameter to give a unit for rounding such as CHF 0.05 for Swiss
invoices

In Settings -> Configuration -> Accounting you will find 2 new types of
rounding

- `Swedish Round globally`

  To round your invoice total amount, this option will do the adjustment in
  the most important tax line of your invoice.

- `Swedish Round by adding an invoice line`

  To round your invoice total amount, this option create a invoice line without
  taxes on it. This invoice line is tagged as `is_rounding`

You can choose the account on which the invoice line will be written

.. _Swedish rounding : https://en.wikipedia.org/wiki/Swedish_rounding
""",
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'license': 'AGPL-3',
 'depends': ['account'],
 'data': ['res_config_view.xml'],
 'test': [],
 'installable': False,
 'auto_install': False,
 'application': True,
 }
