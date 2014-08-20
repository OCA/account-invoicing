# -*- encoding: utf-8 -*-
# #############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
    'name': 'Unique Supplier Invoice Number in Invoice',
    "version": "1.0",
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'description': """
Unique Supplier Invoice Number
==============================

This module adds a insensitive constraint on the supplier_invoice_number field:
(partner_id, supplier_invoice_number) must be unique.

Contributors
------------
* Marc Cassuto (marc.cassuto@savoirfairelinux.com)
* Mathieu Benoit (mathieu.benoit@savoirfairelinux.com)
    """,
    'depends': [
        'account'
    ],
    'installable': False,
}
