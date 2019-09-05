# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def get_taxes_values(self):
        vals = {}
        for line in self.invoice_line_ids:
            vals[line] = {
                'price_unit': line.price_unit,
                'discount': line.discount,
            }
            price_unit = line._get_discounted_price_unit()
            line.update({
                'price_unit': price_unit,
                'discount': 0.0,
            })
        tax_grouped = super(AccountInvoice, self).get_taxes_values()
        for line in self.invoice_line_ids:
            line.update(vals[line])
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

    def _get_discounted_price_unit(self):
        """Inheritable method for getting the unit price after applying
        discount(s).

        :returns: Unit price after discount(s).
        :rtype: float
        """
        self.ensure_one()
        price_unit = self.price_unit
        if self.discount:
            price_unit *= (1 - self.discount / 100)
        if self.discount2:
            price_unit *= (1 - self.discount2 / 100.0)
        if self.discount3:
            price_unit *= (1 - self.discount3 / 100.0)
        return price_unit

    @api.multi
    @api.depends('discount2', 'discount3')
    def _compute_price(self):
        for line in self:
            prev_price_unit = line.price_unit
            prev_discount = line.discount
            price_unit = line._get_discounted_price_unit()
            line.update({
                'price_unit': price_unit,
                'discount': 0.0,
            })
            super(AccountInvoiceLine, line)._compute_price()
            line.update({
                'price_unit': prev_price_unit,
                'discount': prev_discount,
            })
