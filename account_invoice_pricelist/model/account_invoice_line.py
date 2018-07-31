# -*- coding: utf-8 -*-
# © 2015-2016 GRAP <http://www.grap.coop>.
# © 2017 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later <http://www.gnu.org/licenses/agpl.html>.
from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def product_id_change(
            self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None):
        """Make sure pricelist is used on product."""
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id,
            company_id=company_id
        )
        if not product:
            return res
        context = self._context
        partner = self.env['res.partner'].browse(partner_id)
        pricelist_id = context.get('pricelist_id', False)
        if not pricelist_id:
            # If pricelist is not set on invoice, or not available in the
            # context, use the pricelist of the partner
            pricelist_id = partner._get_pricelist_for_invoice(type).id

        if not pricelist_id:
            return res
        company_id = company_id or context.get('company_id', False)
        self = self.with_context(
            company_id=company_id, force_company=company_id
        )
        pricelist_model = self.env['product.pricelist']
        product_model = self.env['product.product']
        product = product_model.browse(product)
        pricelist = pricelist_model.browse(pricelist_id)
        values = res['value']
        if ('uos_id' in values and values['uos_id'] and
                values['uos_id'] != product.uom_id.id):
            pricedict = pricelist.with_context(
                uom=values['uos_id']
            ).price_get(product.id, qty, partner_id)
        else:
            pricedict = pricelist.price_get(product.id, qty, partner_id)
        price_unit = pricedict[pricelist_id]

        # Call _fix_tax_included_price to handled correcty fiscal position
        if type in ('out_invoice', 'out_refund'):
            taxes = product.taxes_id
        else:
            taxes = product.supplier_taxes_id

        price_unit = self.env['account.tax']._fix_tax_included_price(
            price_unit, taxes, values['invoice_line_tax_id'])

        # Apply currency algorithm
        if currency_id:
            company = self.env['res.company'].browse(company_id)
            currency = self.env['res.currency'].browse(currency_id)
            if company.currency_id != currency:
                price_unit = pricelist.currency_id.compute(
                    price_unit, currency, round=True
                )
                price_unit = currency.round(price_unit)
        res['value']['price_unit'] = price_unit
        return res

    @api.multi
    def update_from_pricelist(self):
        """overwrite current prices from pricelist"""
        for this in self:
            if this.invoice_id.state != 'draft':
                continue  # Should only be valid for draft invoices
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
