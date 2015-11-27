# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Savoir-faire Linux. All Rights Reserved.
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
###############################################################################

{
    'name': 'Account Invoice Sale Origin',
    'version': '1.1',
    'category': 'Finance',
    'description': """

    This module displays the origin field of account invoice lines and populate
    it when a customer invoice is create from a sale order.

Contributors
------------
* David Cormier (david.cormier@savoirfairelinux.com)
* Marc Cassuto (marc.cassuto@savoirfairelinux.com)
    """,
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'http://www.savoirfairelinux.com/',
    'depends': ['account', 'sale'],
    'data': [
        'account_invoice_view.xml',
    ],
    'test': [
    ],
    'demo': [],
    'installable': True,
    'active': False,
    'certificate': False,
}
