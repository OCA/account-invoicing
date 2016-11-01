# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def product_id_change(
            self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None
    ):
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty,
            name=name, type=type, partner_id=partner_id,
            fposition_id=fposition_id, price_unit=price_unit,
            currency_id=currency_id,  company_id=company_id
        )
        if product:
            product_model = self.env['product.product']
            if self.user_has_groups(
                    'account_invoice_line_description.'
                    'group_use_product_description_per_inv_line',
            ):
                lang = self.env['res.partner'].browse(partner_id).lang
                product = product_model.with_context(lang=lang).browse(product)
                description = ((product.description_sale
                               if type in ('out_invoice', 'out_refund')
                               else product.description_purchase) or
                               product.description)
                if description:
                    if 'value' not in res:
                        res['value'] = {}
                    res['value']['name'] = description
        return res
