# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Fernando.Rangel (fernando.rangel@vauxoo.com)
#
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
#

{
    "name": "Invoice number",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Localization",
    "description" : """
Invoice number:
===============
   
supplier_invoice_number field added in the tree and search view by
inheritance
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": ["view/invoice_number.xml"],
    "installable": True,
    "active": False,
}
