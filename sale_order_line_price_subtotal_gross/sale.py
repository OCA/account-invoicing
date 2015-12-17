# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2015 initOS GmbH (<http://www.initos.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_subtotal_gross = fields.\
        Float(string='Subtotal gross', digits=dp.get_precision('Account'),
              compute='_amount_line_gross', readonly=True)

    @api.one
    @api.depends('price_unit', 'discount', 'product_uom_qty', 'product_id',
                 'tax_id', 'order_id.partner_id', 'order_id.pricelist_id.currency_id')
    def _amount_line_gross(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        qty = self.product_uom_qty
        taxes = self.tax_id.compute_all(price, qty, self.product_id,
                                       self.order_id.partner_id)
        self.price_subtotal_gross=self.order_id.pricelist_id.currency_id.\
            round(taxes['total_included'])
