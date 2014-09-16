# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
#    Author: Lorenzo Battistini <lorenzo.battistini@agilebg.com>
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
    "name": "Unit of Sale for invoices",
    "version": "1.0",
    "author": "Agile Business Group",
    "website": "http://www.agilebg.com",
    'license': 'AGPL-3',
    "category": "Account",
    "depends": [
        'sale',
    ],
    "description": """
The module displays the UoS and related quantity on invoice lines, retrieving
them from linked sale order(s)

Contributors
------------

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Alex Comba <alex.comba@agilebg.com>
""",
    "demo": [],
    "data": [
        'account_invoice_line_view.xml',
    ],
    'test': [
        'test/account_invoice_line.yml',
    ],
    'installable': True,
}
