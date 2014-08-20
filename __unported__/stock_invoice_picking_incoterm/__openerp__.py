# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    @author Alex Comba <alex.comba@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Stock Invoice Picking Incoterm",
    'version': '0.1',
    'category': 'Warehouse Management',
    'description': """
This module adds the field incoterm to invoice and picking. In this way the
user can specify the incoterm directly on these documents, with no need to
refer to the incoterm of the order (which could even be missing).
The module extends 'stock_invoice_picking' so that the invoices created
from pickings will have the same incoterm set in the picking.
""",
    'author': 'Agile Business Group',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'stock_invoice_picking',
    ],
    'data': [
        'account_invoice_view.xml',
        'stock_view.xml',
    ],
    'test': [
        'test/invoice_picking_incoterm.yml',
    ],
    'installable': False
}
