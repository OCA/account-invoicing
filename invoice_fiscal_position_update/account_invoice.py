# -*- coding: utf-8 -*-
#############################################################################
#
#    Invoice Fiscal Position Update module for OpenERP
#    Copyright (C) 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Mathieu Vatel <mathieu _at_ julius.fr>
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp.osv import orm
from openerp.tools.translate import _


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def update_fiscal_position(self, cr, uid, ids, context=None):
        '''Function executed by the "(update)" button on invoices
        If the invoices are in draft state, it updates taxes and accounts
        on all invoice lines'''
        fp_obj = self.pool['account.fiscal.position']
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.state != 'draft':
                raise orm.except_orm(
                    _('Error:'),
                    _('You cannot update the fiscal position because the '
                        'invoice is not in draft state.'))
            fp = invoice.fiscal_position
            for line in invoice.invoice_line:
                if line.product_id:
                    product = self.pool['product.product'].browse(
                        cr, uid, line.product_id.id, context=context)
                    if invoice.type in ('out_invoice', 'out_refund'):
                        account_id = product.property_account_income.id or \
                            product.categ_id.property_account_income_categ.id
                        taxes = product.taxes_id
                    else:
                        account_id = product.property_account_expense.id or \
                            product.categ_id.property_account_expense_categ.id
                        taxes = product.supplier_taxes_id
                    taxes = taxes or (
                        account_id
                        and self.pool['account.account'].browse(
                            cr, uid, account_id, context=context).tax_ids
                        or False)
                    account_id = fp_obj.map_account(
                        cr, uid, fp, account_id, context=context)
                    tax_ids = fp_obj.map_tax(
                        cr, uid, fp, taxes, context=context)

                    line.write({
                        'invoice_line_tax_id': [(6, 0, tax_ids)],
                        'account_id': account_id,
                        })
        return True
