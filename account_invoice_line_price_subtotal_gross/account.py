# -*- coding: utf-8 -*-
# © 2015 initOS GmbH (<http://www.initos.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    price_subtotal_gross = fields. \
        Float(string='Amount gross', digits=dp.get_precision('Account'),
              compute='_compute_price_gross', store=True, readonly=True,)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
                 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id')
    def _compute_price_gross(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id. \
            compute_all(price, self.quantity, product=self.product_id,
                        partner=self.invoice_id.partner_id)
        self.price_subtotal_gross = taxes['total_included']
        if self.invoice_id:
            self.price_subtotal_gross = self.invoice_id.currency_id. \
                round(self.price_subtotal_gross)
