# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017-today Ascetic Business Solution <www.asceticbs.com>
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
#################################################################################

{
    'name': "Split Invoice",
    'author': 'Zadsolutions, Ahmed Salama',    'category': 'Account',
    'summary': """Split Invoice/Bill""",
    'website': 'http://www.zadsolutions.com',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '10.0',
    'depends': ['base','account'],
    'data': ['security/show_allow_split_invoice.xml','views/account_invoice_view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
