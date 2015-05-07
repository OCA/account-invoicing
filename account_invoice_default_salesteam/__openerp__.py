# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
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
###############################################################################

{
    'name': 'Default Sales Team on Invoice',
    'version': '1.1',
    'category': 'Accounting & Finance',
    'description': """
This module set the Sales Team (section_id field) in the 2 following scenarios:

* when creating an invoice, set on partner_id.onchange() from the partner's
  Sales Team
* when invoicing from sales_order, set from the Sales Order's Sales Team.
""",
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'http://www.savoirfairelinux.com',
    'images': [],
    'depends': [
        'sale_crm',
        'stock'
    ],
    'data': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
}
