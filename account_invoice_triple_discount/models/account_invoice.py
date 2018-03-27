# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    @api.v8
    def compute(self, invoice):
        vals = {}
        for line in invoice.invoice_line:
            vals[line] = {
                'price_unit': line.price_unit,
                'discount': line.discount,
            }
            line.update({
                'price_unit': line.price_unit_with_discount(),
                'discount': 0.0,
            })
        res = super(AccountInvoiceTax, self).compute(invoice)
        for line in invoice.invoice_line:
            line.update(vals[line])
        return res


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
    def price_unit_with_discount(self):
        self.ensure_one()
        return self.price_unit *\
            (1 - (self.discount or 0.0) / 100.0) *\
            (1 - (self.discount2 or 0.0) / 100.0) *\
            (1 - (self.discount3 or 0.0) / 100.0)

    @api.multi
    @api.depends('discount2', 'discount3')
    def _compute_price(self):
        for line in self:
            prev_price_unit = line.price_unit
            prev_discount = line.discount
            line.update({
                'price_unit': line.price_unit_with_discount(),
                'discount': 0.0,
            })
            super(AccountInvoiceLine, line)._compute_price()
            line.update({
                'price_unit': prev_price_unit,
                'discount': prev_discount,
            })
