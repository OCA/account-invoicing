# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author: Ian Li <ian.li@elico-corp.com>
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
    'name': 'Account Invoice Merge Wizard',
    'version': '1.1.1',
    'category': 'Finance',
    'description': """
This module adds an action in the invoices lists to merge of invoices. Here are
the condition to allow merge:

- Type should be the same (customer Invoice, supplier invoice, Customer or
  Supplier Refund)
- Partner should be the same
- Currency should be the same
- Account receivable account should be the same
    """,
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn',
    'depends': ['account'],
    'data': [
        'wizard/invoice_merge_view.xml',
    ],
    'test': [
    ],
    'demo': [],
    'installable': False,
    'active': False,
    'certificate': False,
}
