# -*- coding: utf-8 -*-
##############################################################################

#     This file is part of account_invoice_line_sort, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_line_sort is free software: you can redistribute it
#     and/or modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     account_invoice_line_sort is distributed in the hope that it will
#     be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with account_invoice_line_sort.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Sort Customer Invoice Lines",

    'summary': """
        Manage sort of customer invoice lines by customers""",

    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://acsone.eu",

    'category': 'Finance',
    'version': '0.1',
    'license': 'AGPL-3',

    'depends': [
        'account',
    ],

    'data': [
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml'
    ],

    'demo': [
    ],
}
