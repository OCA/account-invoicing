# -*- coding: utf-8 -*-
# © 2015 initOS GmbH (<http://www.initos.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_subtotal_gross = fields.\
        Float(string='Subtotal gross', digits=dp.get_precision('Account'),
              compute='_amount_line_gross', readonly=True)

    @api.one
    @api.depends('price_unit', 'discount', 'product_uom_qty', 'product_id',
                 'tax_id', 'order_id.partner_id',
                 'order_id.pricelist_id.currency_id')
    def _amount_line_gross(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        qty = self.product_uom_qty
        taxes = self.tax_id.compute_all(price, qty, self.product_id,
                                        self.order_id.partner_id)
        self.price_subtotal_gross = self.order_id.pricelist_id.currency_id. \
            round(taxes['total_included'])
