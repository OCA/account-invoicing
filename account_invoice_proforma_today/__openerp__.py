# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 OpenERP s.a. (<http://openerp.com>).
#    Copyright (C) 2015 initOS GmbH (<http://www.initos.com>).
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
    'name': 'Account Invoice Proforma Today',
    'version': '0.1',
    'author': 'initOS GmbH',
    'category': '',
    'description':
    """
    The modul extends the account.invoice model to set the date of the invoice as the today's date when changing state from 'proforma' to 'open'.
    """,
    'website': 'http://www.initos.com',
    'license': 'AGPL-3',
    'images': [],
    'depends': ['account',
                ],
    'data': [
    ],
    'js': [
    ],
    'qweb': [
    ],
    'css': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'active': False,
    'installable': True
}
