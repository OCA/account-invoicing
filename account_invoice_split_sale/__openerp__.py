# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_split_sale,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_split_sale is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_split_sale is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_split_sale.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Account Invoice Split Sale",
    'summary': """
        Provide a compatibility between sale workflow and
        Account Invoice Split""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Finance',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_split',
        'sale',
        'base_suspend_security',
    ],
    'auto_install': True,
}
