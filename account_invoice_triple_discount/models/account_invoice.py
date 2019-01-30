# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def get_taxes_values(self):
        prev_values = self.invoice_line_ids.triple_discount_preprocess()
        tax_grouped = super(AccountInvoice, self).get_taxes_values()
        self.env['account.invoice.line'].triple_discount_postprocess(
            prev_values)
        return tax_grouped


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
    @api.depends('discount2', 'discount3')
    def _compute_price(self):
        prev_values = self.triple_discount_preprocess()
        super(AccountInvoiceLine, self)._compute_price()
        self.triple_discount_postprocess(prev_values)

    def _get_triple_discount(self):
        """Get the discount that is equivalent to the subsequent application
        of discount, discount2 and discount3"""
        discount_factor = 1.0
        for discount in [self.discount, self.discount2, self.discount3]:
            discount_factor *= (100.0 - discount) / 100.0
        return 100.0 - (discount_factor * 100.0)

    @api.multi
    def triple_discount_preprocess(self):
        """Save the values of the discounts in a dictionary,
        to be restored in postprocess.
        Resetting discount2 and discount3 to 0.0 avoids issues if
        this method is called multiple times.
        Updating the cache provides consistency through recomputations."""
        prev_values = dict()
        self.invalidate_cache(
            fnames=['discount', 'discount2', 'discount3'],
            ids=self.ids)
        for line in self:
            prev_values[line] = dict(
                discount=line.discount,
                discount2=line.discount2,
                discount3=line.discount3,
            )
            line._cache.update({
                'discount': line._get_triple_discount(),
                'discount2': 0.0,
                'discount3': 0.0
            })
        return prev_values

    @api.model
    def triple_discount_postprocess(self, prev_values):
        """Restore the discounts of the lines in the dictionary prev_values.
        Updating the cache provides consistency through recomputations."""
        self.invalidate_cache(
            fnames=['discount', 'discount2', 'discount3'],
            ids=[l.id for l in prev_values.keys()])
        for line, prev_vals_dict in prev_values.items():
            line._cache.update(prev_vals_dict)
