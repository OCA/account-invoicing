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
        'Margin', compute='_compute_margin', store=True,
        digits_compute=dp.get_precision('Product Price'),
        help="It gives profitability by calculating the difference between"
        " the Unit Price and the cost price.")

    # Compute Section
    @api.multi
    @api.depends('invoice_line.margin')
    def _compute_margin(self):
        for invoice in self:
            invoice.margin = sum(invoice.mapped('invoice_line.margin'))
