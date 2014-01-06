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

    def fiscal_position_change(
            self, cr, uid, ids, fiscal_position, type, invoice_line,
            context=None):
        '''Function executed by the on_change on the fiscal_position field
        of invoice ; it updates taxes and accounts on all invoice lines'''
        assert len(ids) in (0, 1), 'One ID max'
        fp_obj = self.pool['account.fiscal.position']
        res = {}
        iline_dict = self.resolve_2many_commands(
            cr, uid, 'invoice_line', invoice_line, context=context)
        lines_without_product = []
        if fiscal_position:
            fp = fp_obj.browse(cr, uid, fiscal_position, context=context)
        else:
            fp = False
        for line in iline_dict:
            # Reformat iline_dict so as to be compatible with what is
            # accepted in res['value']
            for key, value in line.iteritems():
                if isinstance(value, tuple) and len(value) == 2:
                    if (isinstance(value[0], int)
                            and isinstance(value[1], (str, unicode))):
                        line[key] = value[0]
            if line.get('product_id'):
                product = self.pool['product.product'].browse(
                    cr, uid, line.get('product_id'), context=context)
                if type in ('out_invoice', 'out_refund'):
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
                lines_without_product.append(line.get('name'))
        res['value'] = {}
        res['value']['invoice_line'] = iline_dict

        if lines_without_product:
            res['warning'] = {'title': _('Warning')}
            if len(lines_without_product) == len(iline_dict):
                res['warning']['message'] = _(
                    "The invoice lines were not updated to the new "
                    "Fiscal Position because they don't have products.\n"
                    "You should update the Account and the Taxes of each "
                    "invoice line manually.")
            else:
                display_line_names = ''
                for name in lines_without_product:
                    display_line_names += "- %s\n" % name
                res['warning']['message'] = _(
                    "The following invoice lines were not updated "
                    "to the new Fiscal Position because they don't have a "
                    "Product:\n %s\nYou should update the Account and the "
                    "Taxes of these invoice lines manually."
                    ) % display_line_names,
        return res
