# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
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
    "name": "Free Invoice Lines",
    "description": """This module adds 'for free' field to the invoice lines""",
    "version": "0.1",
    "depends": ['account'],
    "category": "Accounting & Finance",
    "author": "Andrea Cometa",
    "url": "http://www.andreacometa.it",
    "data": [
        'account/account_view.xml',
        ],
    "installable": True,
    "auto_install": False,
    "certificate": "",
    'images': [],
}
