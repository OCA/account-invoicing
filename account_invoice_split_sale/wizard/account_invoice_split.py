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

from openerp import models, api


class AccountInvoiceSplit(models.TransientModel):
    _inherit = 'account.invoice.split'

    @api.model
    def _create_invoice(self, vals):
        new_invoice = super(AccountInvoiceSplit, self)._create_invoice(vals)
        so = self.env['sale.order'].search([('order_line.invoice_lines', 'in',
                                             new_invoice.invoice_line.ids)])
        so.write({'invoice_ids': [(4, new_invoice.id)]})
        # Reevaluates sale order workflow instance
        so.step_workflow()
        return new_invoice


class AccountInvoiceSplitLine(models.TransientModel):
    _inherit = 'account.invoice.split.line'

    @api.multi
    def _create_invoice_line(self):
        new_invoice_line = \
            super(AccountInvoiceSplitLine, self)._create_invoice_line()
        so_lines = self.env['sale.order.line']\
            .search([('invoice_lines', 'in',
                      [self.origin_invoice_line_id.id])])
        so_lines.write({'invoice_lines': [(4, new_invoice_line.id)]})
        return new_invoice_line
