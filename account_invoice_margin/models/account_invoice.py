# -*- coding: utf-8 -*-
# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    margin = fields.Float(
        compute='_compute_margin',
        digits=dp.get_precision('Product Price'),
        store=True,
        string='Margin',
    )
    margin_signed = fields.Float(
        compute='_compute_margin',
        digits=dp.get_precision('Product Price'),
        store=True,
        string='Margin Signed',
    )
    margin_percent = fields.Float(
        string='% Margin',
        compute='_compute_margin',
        store=True,
        readonly=True,
    )
    purchase_price = fields.Float(
        digits=dp.get_precision('Product Price'),
        string='Cost',
    )

    @api.multi
    @api.depends('purchase_price', 'price_subtotal')
    def _compute_margin(self):
        for line in self.filtered(lambda x: x.invoice_id.type[:2] != 'in'):
            tmp_margin = line.price_subtotal - (
                line.purchase_price * line.quantity)
            sign = line.invoice_id.type in [
                'in_refund', 'out_refund'] and -1 or 1
            line.update({
                'margin': tmp_margin,
                'margin_signed': tmp_margin * sign,
                'margin_percent': (tmp_margin / line.price_subtotal * 100.0 if
                                   line.price_subtotal else 0.0),
            })

    @api.onchange('product_id', 'uom_id')
    def _onchange_product_id_account_invoice_margin(self):
        if self.invoice_id.type in ['out_invoice', 'out_refund']:
            purchase_price = self.product_id.standard_price
            if any(self.product_id.supplier_taxes_id.mapped('price_include')):
                taxes = self.product_id.supplier_taxes_id.compute_all(
                    purchase_price, self.invoice_id.currency_id, 1,
                    product=self.product_id,
                    partner=self.invoice_id.partner_id)
                purchase_price = taxes['total_excluded']
            if self.uom_id != self.product_id.uom_id:
                purchase_price = self.product_id.uom_id._compute_price(
                    self.product_id.uom_id.id, purchase_price, self.uom_id.id)
            self.purchase_price = purchase_price
