# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_split_sale_stock,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_split_sale_stock is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_split_sale_stock is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_split_sale_stock.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api
from openerp.tools import SUPERUSER_ID


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def confirm_paid(self):
        """ Reevaluates sale order workflow instance at invoice payment"""
        res = super(AccountInvoice, self).confirm_paid()
        so_obj = self.env['sale.order']
        # read access on purchase.order object is not required
        if not so_obj.check_access_rights('read', raise_exception=False):
            user_id = SUPERUSER_ID
        else:
            user_id = self._uid
        so = so_obj.sudo(user=user_id)\
            .search([('invoice_ids', 'in', self.ids)])
        so.step_workflow()
        return res
