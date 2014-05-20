# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alex Comba <alex.comba@agilebg.com>
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
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
    'name': "Invoice line no picking name",
    'version': '0.1',
    'category': 'Generic Modules/Accounting',
    'description': """
This module allows to not use the picking name on the invoice lines.
To do so, the user has to belong to
group_not_use_picking_name_per_invoice_line.
This is possible by selecting the related option in the following menu:

Settings --> Configuration --> Warehouse --> Products
    """,
    'author': 'Agile Business Group',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": [
        'sale_stock',
    ],
    "data": [
        'security/invoice_security.xml',
        'res_config_view.xml',
    ],
    'test': [
        'test/invoice_line_no_picking_name.yml',
    ],
    "installable": True
}
