# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-Guillaume (Camptocamp)
#    Copyright 2010 Camptocamp SA
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
    'name': 'Add "To Send" and "To Validate" states in Invoices',
    'version': '1.0',
    'category': 'Generic Modules/Invoicing',
    'description':
    '''
This module adds 2 states between draft and open state in invoices:

- To Validate: For invoices which need a validation
- To Send: For all invoices that need to be sent

''',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'website': 'http://camptocamp.com',
    'depends': ['account'],
    'data': [
        'invoice_wkf.xml',
        'invoice_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False
}
