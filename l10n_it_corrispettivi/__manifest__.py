# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    'name': 'Italian Localisation - Corrispettivi',
    'version': '0.1',
    'category': 'Localisation/Italy',
    'description': """This module helps to easily input Corrispettivi within OpenERP.

Per maggiori informazioni:
http://planet.domsense.com/2011/11/openerp-registrare-i-corrispettivi/""",
    'author': "OpenERP Italian Community,Odoo Community Association (OCA)",
    'website': 'http://www.openerp-italia.org',
    'license': 'AGPL-3',
    "depends": ['account_voucher'],
    "data": [
            'partner_data.xml',
        'account_view.xml',
        'installer_view.xml',
    ],
    "active": False,
    "installable": True
}
