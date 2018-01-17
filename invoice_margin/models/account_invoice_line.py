# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # Columns Section
    margin = fields.Float(
        'Margin', compute='_compute_multi_margin', store=True,
        multi='multi_margin',
        digits_compute=dp.get_precision('Product Price'))

    margin_percent = fields.Float(
        'Margin (%)', compute='_compute_multi_margin', store=True,
        multi='multi_margin',
        digits_compute=dp.get_precision('Product Price'))

    purchase_price = fields.Float(
        string='Cost Price', copy=False,
        digits_compute=dp.get_precision('Product Price'))

    # Onchange Section
    @api.multi
    def product_id_change(
            self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None):
        product_obj = self.env['product.product']
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        if product:
            prod = product_obj.browse(product)
            res['value']['purchase_price'] = prod.standard_price
        return res

    # Compute Section
    @api.multi
    @api.depends(
        'purchase_price', 'quantity', 'price_subtotal', 'invoice_id.type')
    def _compute_multi_margin(self):
        for line in self.filtered(
                lambda l: l.product_id and
                l.invoice_id.type in ('out_invoice', 'out_refund')):
            line.purchase_price = line.product_id.standard_price
            tmp_margin =\
                line.price_subtotal - (line.purchase_price * line.quantity)
            line.update({
                'margin': tmp_margin,
                'margin_percent': (
                    tmp_margin / line.price_subtotal * 100.0 if
                        line.price_subtotal else 0.0),
            })

    # Overload Section. Necessary for lines created by other way than UI
    # Could be remove in the version of Odoo that removed product_id_change
    # function
    @api.model
    def create(self, vals):
        if not vals.get('purchase_price', False):
            product_obj = self.env['product.product']
            product = product_obj.browse(vals.get('product_id'))
            vals['purchase_price'] = product.standard_price
        return super(AccountInvoiceLine, self).create(vals)
