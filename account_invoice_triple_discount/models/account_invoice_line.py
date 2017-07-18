# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    discount2 = fields.Float(
        'Discount 2 (%)',
        digits=dp.get_precision('Discount'),
        default=0.0,
    )
    discount3 = fields.Float(
        'Discount 3 (%)',
        digits=dp.get_precision('Discount'),
        default=0.0,
    )

    @api.multi
    @api.depends('price_unit', 'discount', 'discount2', 'discount3',
                 'invoice_line_tax_ids', 'quantity', 'product_id',
                 'invoice_id.partner_id', 'invoice_id.currency_id',
                 'invoice_id.company_id', 'invoice_id.date_invoice')
    def _compute_price(self):
        for line in self:
            price = line.price_unit
            discount = line.discount
            line.price_unit *= (1 - (line.discount or 0.0) / 100.0)
            line.price_unit *= (1 - (line.discount2 or 0.0) / 100.0)
            line.price_unit *= (1 - (line.discount3 or 0.0) / 100.0)
            line['discount'] = 0.0
            super(AccountInvoiceLine, line)._compute_price()
            line['price_unit'] = price
            line['discount'] = discount
