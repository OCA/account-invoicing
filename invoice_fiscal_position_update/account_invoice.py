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

    @api.onchange('fiscal_position')
    def fiscal_position_change(self):
        """Updates taxes and accounts on all invoice lines"""
        self.ensure_one()
        AccountTax = self.env['account.tax']
        res = {}
        lines_without_product = []
        fp = self.fiscal_position
        inv_type = self.type
        for line in self.invoice_line:
            if line.product_id:
                product = line.product_id
                if inv_type in ('out_invoice', 'out_refund'):
                    account = (
                        product.property_account_income or
                        product.categ_id.property_account_income_categ)
                    taxes = product.taxes_id
                else:
                    account = (
                        product.property_account_expense or
                        product.categ_id.property_account_expense_categ)
                    taxes = product.supplier_taxes_id
                taxes = taxes or account.tax_ids
                if fp:
                    account = fp.map_account(account)
                    taxes = fp.map_tax(taxes)

                line.price_unit = AccountTax._fix_tax_included_price(
                    line.price_unit,
                    line.invoice_line_tax_id,
                    taxes.ids)
                line.invoice_line_tax_id = [(6, 0, taxes.ids)]
                line.account_id = account.id
            else:
                lines_without_product.append(line.name)

        if lines_without_product:
            res['warning'] = {'title': _('Warning')}
            if len(lines_without_product) == len(self.invoice_line):
                res['warning']['message'] = _(
                    "The invoice lines were not updated to the new "
                    "Fiscal Position because they don't have products.\n"
                    "You should update the Account and the Taxes of each "
                    "invoice line manually.")
            else:
                res['warning']['message'] = _(
                    "The following invoice lines were not updated "
                    "to the new Fiscal Position because they don't have a "
                    "Product:\n- %s\nYou should update the Account and the "
                    "Taxes of these invoice lines manually."
                ) % ('\n- '.join(lines_without_product))
        return res
