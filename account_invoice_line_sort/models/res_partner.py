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

from openerp import models, fields
from . import account_invoice


class res_partner(models.Model):
    _inherit = "res.partner"

    line_order = fields.Selection(account_invoice.AVAILABLE_SORT_OPTIONS,
                                  "Sort Invoice Lines By",
                                  default='sequence')
    line_order_direction = fields.Selection(
        account_invoice.AVAILABLE_ORDER_OPTIONS,
        "Sort Direction",
        default='asc')
