# -*- coding: utf-8 -*-
##############################################################################
#
#    Invoice Fiscal Position Update module for OpenERP
#    Copyright (C) 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
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
    'name': 'Invoice Fiscal Position Update',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Update the fiscal position of an invoice in one click',
    'description': """
Invoice Fiscal Position Update
==============================

When the invoice is in draft state, you can change the fiscal position and click on a button *(update)* next to the fiscal position to update the taxes and the accounts on all the invoice lines which have a product (the invoice lines without a product are not updated).
""",
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr/',
    'depends': ['account'],
    'data': ['account_invoice_view.xml'],
    'images': ['images/invoice_fiscal_position_update.jpg'],
    'installable': True,
    'active': False,
}
