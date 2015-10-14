# -*- coding: utf-8 -*-
##############################################################################
#
# This file is part of account_invoice_period_usability,
# an Odoo module.
#
# Authors: ACSONE SA/NV (<http://acsone.eu>)
#
# account_invoice_period_usability is free software:
# you can redistribute it and/or modify it under the terms of the GNU
# Affero General Public License as published by the Free Software
# Foundation,either version 3 of the License, or (at your option) any
# later version.
#
# account_invoice_period_usability is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with account_invoice_period_usability.
# If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Account Invoice Period Usability',
    'summary': """
Display in the supplier invoice form the fiscal period
next to the invoice date""",
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'http://www.acsone.eu',
    'category': 'Accounting & Finance',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
}
