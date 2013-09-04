# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
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
    "name": "Invoice Shipping Address",
    "version": "0.1",
    'category': 'Generic Modules/Accounting',
    "depends": ["account", "sale"],
    "author": "Andrea Cometa",
    "description": """This module adds a shipping address field to the invoice and tries to fill it automatically""",
    'website': 'http://www.andreacometa.it',
    'init_xml': [],
    'update_xml': [
        'invoice_view.xml',
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
