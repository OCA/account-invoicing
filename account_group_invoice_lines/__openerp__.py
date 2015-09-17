# -*- coding: utf-8 -*-
##############################################################################
#
#    account_group_invoice_lines module for Odoo
#    Copyright (C) 2012-2015 SYLEAM Info Services (<http://www.syleam.fr/>)
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author: Sébastien LANGE <sebastien.lange@syleam.fr>
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Account Group Invoice Lines',
    'version': '1.1.0',
    'category': 'Accounting & Finance',
    'summary': 'Add option to group invoice line per account',
    'author': 'SYLEAM,Akretion,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'http://www.syleam.fr/',
    'depends': ['account'],
    'data': ['account_view.xml'],
    'installable': True,
}
