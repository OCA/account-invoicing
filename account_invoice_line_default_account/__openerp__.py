# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
#    This module copyright (C) 2013-2015 BCIM SPRL (<http://www.bcim.be>).
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
    'name': 'Account Invoice Line Default Account',
    'version': '1.0',
    'depends': [
        'account'
    ],
    'author': 'Therp BV,BCIM,Odoo Community Association (OCA)',
    'contributors': ['Jacques-Etienne Baudoux <je@bcim.be>'],
    'category': 'Accounting',
    'data': [
        'view/res_partner.xml',
        'view/account_invoice.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
