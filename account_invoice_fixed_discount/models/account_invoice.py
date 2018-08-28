# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def get_taxes_values(self):
        self.ensure_one()
        vals = {}
        for line in self.invoice_line_ids.filtered('discount_fixed'):
            vals[line] = {
                'price_unit': line.price_unit,
                'discount_fixed': line.discount_fixed,
            }
            price_unit = line.price_unit - line.discount_fixed
            line.update({
                'price_unit': price_unit,
                'discount_fixed': 0.0,
            })
        tax_grouped = super(AccountInvoice, self).get_taxes_values()
        for line in vals.keys():
            line.update(vals[line])
        return tax_grouped


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits=dp.get_precision('Product Price'),
        help="Fixed amount discount.")

    @api.onchange('discount')
    def _onchange_discount(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange('discount_fixed')
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.multi
    @api.constrains('discount', 'discount_fixed')
    def _check_only_one_discount(self):
        for line in self:
            if line.discount and line.discount_fixed:
                raise ValidationError(
                    _("You can only set one type of discount per line."))

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date',
                 'discount_fixed')
    def _compute_price(self):
        if not self.discount_fixed:
            return super(AccountInvoiceLine, self)._compute_price()
        prev_price_unit = self.price_unit
        prev_discount_fixed = self.discount_fixed
        price_unit = self.price_unit - self.discount_fixed
        self.update({
            'price_unit': price_unit,
            'discount_fixed': 0.0,
        })
        super(AccountInvoiceLine, self)._compute_price()
        self.update({
            'price_unit': prev_price_unit,
            'discount_fixed': prev_discount_fixed,
        })
