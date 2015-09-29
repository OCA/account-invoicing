# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def product_id_change(
            self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None):
        result = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        values = result.get('value', {})
        if product and 'pricelist_id' in self.env.context:
            # get pricelist price
            values['price_unit'] = self.env['product.product']\
                .browse([product])\
                .with_context(
                    quantity=qty, pricelist=self.env.context['pricelist_id'],
                    partner=partner_id)\
                ._product_price(None, None)\
                .get(product)
            # adjust for currency, uos (taken from super)
            if company_id and currency_id:
                company = self.env['res.company'].browse([company_id])
                product = self.env['product.product'].browse([product])
                currency = self.env['res.currency'].browse([currency_id])
                if company.currency_id != currency:
                    if type in ('in_invoice', 'in_refund'):
                        values['price_unit'] = product.standard_price
                    values['price_unit'] = values['price_unit'] * currency.rate

                if values['uos_id'] and values['uos_id'] != product.uom_id.id:
                    values['price_unit'] = self.env['product.uom']\
                        ._compute_price(product.uom_id.id,
                                        values['price_unit'], values['uos_id'])
        return result

    @api.multi
    def update_from_pricelist(self):
        """overwrite current prices from pricelist"""
        for this in self:
            values = this\
                .with_context(pricelist_id=this.invoice_id.pricelist_id.id)\
                .product_id_change(
                    this.product_id.id, this.uos_id.id, qty=this.quantity,
                    name=this.name, type=this.invoice_id.type,
                    partner_id=this.invoice_id.partner_id.id,
                    fposition_id=this.invoice_id.fiscal_position.id,
                    price_unit=this.price_unit,
                    currency_id=this.invoice_id.currency_id.id,
                    company_id=this.invoice_id.company_id.id)['value']
            this.write({
                'price_unit': values['price_unit'],
            })
