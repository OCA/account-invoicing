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

    purchase_price = fields.Float(
        'Cost Price', compute='_compute_multi_margin', store=True,
        multi='multi_margin',
        digits_compute=dp.get_precision('Product Price'))

    # Compute Section
    @api.multi
    @api.depends('product_id', 'quantity', 'price_subtotal')
    def _compute_multi_margin(self):
        for line in self:
            if not line.product_id or\
                    line.invoice_id.type not in ('out_invoice', 'out_refund'):
                line.purchase_price = 0
                line.margin = 0
            else:
                line.purchase_price = line.product_id.standard_price
                line.margin = line.price_subtotal - (
                    line.product_id.standard_price * line.quantity)
