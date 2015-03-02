# -*- coding: utf-8 -*-
##############################################################################
#
#    account_invoice_total module for OpenERP
#    Copyright (C) 2012 Ren Dao Solutions (<http://rendaosolutions.com>).
#    Copyright (C) 2012 Acsone (<http://acsone.eu>).
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
{   'name': 'Total Field on Supplier Invoice',
    'version': '0.1',
    'category': 'Accounting',
    'description': """
Since OpenERP 6.1 the check_total field in the supplier invoice form, and the corresponding
check, has been removed. This module brings back the functionality from 6.0 and before.

See discussion : https://bugs.launchpad.net/openobject-addons/+bug/998008
See revision : http://bazaar.launchpad.net/~openerp/openobject-addons/trunk/revision/6254

In OpenERP 7.0, this module has been superseded by a configurable setting. Go to
Settings/configuration/accounting and tick the boolean "Check the total of supplier invoices"
in the section "eInvoicing & Payments"
    """,
    'author': "Ren Dao Solutions bvba, ACSONE SA/NV,Odoo Community Association (OCA)",
    'depends': [
        'account',
    ],
    'init_xml': [
        'account_invoice_total_view.xml'
    ],
    'update_xml': [],
    'demo_xml': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
