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
from pprint import pprint


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def fiscal_position_change(
            self, cr, uid, ids, fiscal_position, invoice_line, context=None):
        '''Function executed by the on_change on the fiscal_position field
        of invoice ; it updates taxes and accounts on all invoice lines'''
        fp_obj = self.pool['account.fiscal.position']
        assert len(ids) == 1, 'Only one ID allowed'
        res = {}
        print "invoice_line="
        pprint(invoice_line)
        print "resolve_2many_commands="
        il_r2c = self.resolve_2many_commands(cr, uid, 'invoice_line', invoice_line, context=context)
        pprint(il_r2c)
        lines_without_product = []
        invoice = self.browse(cr, uid, ids[0], context=context)
        if fiscal_position:
            fp = fp_obj.browse(cr, uid, fiscal_position, context=context)
        else:
            fp = False
        for line in il_r2c:
            if line.get('product_id'):
                if isinstance(line.get('product_id'), int):
                    product_id = line.get('product_id')
                else:
                    product_id = line.get('product_id')[0]
                product = self.pool['product.product'].browse(
                    cr, uid, product_id, context=context)
                if invoice.type in ('out_invoice', 'out_refund'):
                    account_id = (
                        product.property_account_income.id or
                        product.categ_id.property_account_income_categ.id)
                    taxes = product.taxes_id
                else:
                    account_id = (
                        product.property_account_expense.id or
                        product.categ_id.property_account_expense_categ.id)
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

                line.update({
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'account_id': account_id,
                    })
            else:
                lines_without_product.append(line.name)
        res['value'] = {}
        res['value']['invoice_line'] = il_r2c

        if lines_without_product:
            display_line_names = ''
            for name in lines_without_product:
                display_line_names += "- %s\n" % name
            res['warning'] = {
                'title': _('Warning'),
                'message': _(
                    "The following invoice lines were not updated "
                    "to the new fiscal position because they don't have a "
                    "product:\n %s\nYou should update these invoice lines "
                    "manually."
                    ) % display_line_names,
            }
        print "res="
        pprint(res)
        return res
