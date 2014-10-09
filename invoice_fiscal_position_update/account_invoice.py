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

from openerp import models, api, _


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def fiscal_position_change(
            self, fiscal_position_id, type, invoice_line):
        '''Function executed by the on_change on the fiscal_position field
        of invoice ; it updates taxes and accounts on all invoice lines'''
        fp_obj = self.env['account.fiscal.position']
        res = {'value': {}}
        line_dict = self.resolve_2many_commands(
            'invoice_line', invoice_line)
        lines_without_product = []
        if fiscal_position_id:
            fp = fp_obj.browse(fiscal_position_id)
        else:
            fp = False
        for line in line_dict:
            # Reformat line_dict so as to be compatible with what is
            # accepted in res['value']
            for key, value in line.iteritems():
                if isinstance(value, tuple) and len(value) == 2:
                    line[key] = value[0]
            if line.get('product_id'):
                product = self.env['product.product'].browse(
                    line.get('product_id'))
                if type in ('out_invoice', 'out_refund'):
                    account = (
                        product.property_account_income or
                        product.categ_id.property_account_income_categ)
                    taxes = product.taxes_id
                else:
                    account = (
                        product.property_account_expense or
                        product.categ_id.property_account_expense_categ)
                    taxes = product.supplier_taxes_id
                taxes = taxes or (
                    account and account.tax_ids or False)
                if fp:
                    account = fp.map_account(account)
                    taxes = fp.map_tax(taxes)

                tax_ids = [tax.id for tax in taxes]
                line.update({
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'account_id': account.id,
                })
            else:
                lines_without_product.append(line.get('name'))
        res['value']['invoice_line'] = line_dict

        if lines_without_product:
            res['warning'] = {'title': _('Warning')}
            if len(lines_without_product) == len(line_dict):
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
