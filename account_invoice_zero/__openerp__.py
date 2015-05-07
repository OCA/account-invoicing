# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

{'name': 'Account Invoice Zero',
 'version': '1.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Accounting & Finance',
 'depends': ['account',
             ],
 'description': """
Account Invoice Zero
====================

Invoices with a amount of 0 are automatically set as paid.

When an invoice has an amount of 0, OpenERP still generates a
receivable/payable move line with a 0 balance.  The invoice stays as
open even if there is nothing to pay.  The user has 2 ways to set the
invoice as paid: create a payment of 0 and reconcile the line with the
payment or reconcile the receivable/payable move line with itself.
This module takes the latter approach and will directly set the invoice
as paid once it is opened.

 """,
 'website': 'http://www.camptocamp.com',
 'data': [],
 'test': ['test/account_invoice_zero_paid.yml',
          'test/account_invoice_no_zero_open.yml',
          ],
 'installable': True,
 'auto_install': False,
 }
