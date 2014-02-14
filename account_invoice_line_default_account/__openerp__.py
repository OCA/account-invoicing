# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
#    This module copyright (C) 2013 BCIM SPRL (<http://www.bcim.be>).
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
    'version': '7.0.1.0',
    'depends': [
        'account'
    ],
    'author': 'Therp BV',
    'contributors': ['Jacques-Etienne Baudoux <je@bcim.be>'],
    'category': 'Accounting',
    'description': '''When entering sales or purchase invoices directly, the
user has to select an account which will be used as a counterpart in the
generated move lines. Each supplier will mostly be linked to one account. For
instance when ordering paper from a supplier that deals in paper, the
counterpart account will mostly be something like 'office expenses'.  The sme
principle has been applied for customers. This module will add a default
counterpart expense and income account to a partner, comparable to the similiar
field in product. When an invoice is entered, withouth a product, the field
from partner will be used as default. Also when an account is entered on an
invoice line (not automatically selected for a product), the account will be
automatically linked to the partner as default expense or income account, unless
explicitly disabled in the partner record.''',
    'data': [
        'view/res_partner.xml',
        'view/account_invoice.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
