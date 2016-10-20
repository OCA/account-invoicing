# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
#    Copyright 2015 Akretion (www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Payment Term Extension',
    'version': '9.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Adds rounding, months and weeks properties on '
               'payment term lines',
    'description': "",
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'maintainer': 'OCA',
    'website': 'http://www.camptocamp.com/',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': ['account_view.xml'],
    'demo': ['account_demo.xml'],
    'test': [],
    'installable': True,
}
