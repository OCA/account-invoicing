# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Columns Section
    margin = fields.Float(
        'Margin', compute='_compute_margin', store=True, multi='margin',
        digits_compute=dp.get_precision('Product Price'),
        help="It gives profitability by calculating the difference between"
        " the Unit Price and the cost price.")

    margin_percent = fields.Float(
        'Margin (%)', compute='_compute_margin', store=True, multi='margin',
        digits_compute=dp.get_precision('PoS Order Margin Percent'))

    # Compute Section
    @api.multi
    @api.depends('invoice_line.margin', 'invoice_line.price_subtotal')
    def _compute_margin(self):
        for invoice in self:
            tmp_margin = sum(invoice.mapped('invoice_line.margin'))
            tmp_subtotal = sum(invoice.mapped('invoice_line.price_subtotal'))
            invoice.update({
                'margin': tmp_margin,
                'margin_percent': tmp_margin / tmp_subtotal * 100 if
                tmp_subtotal else 0.0,
            })
