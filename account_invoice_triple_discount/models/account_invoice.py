# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_unit *= 1 - (line.discount2 or 0.0) / 100.0
            price_unit *= 1 - (line.discount3 or 0.0) / 100.0
            taxes = line.invoice_line_tax_ids.\
                        compute_all(price_unit, self.currency_id,
                                    line.quantity, line.product_id,
                                    self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).\
                    get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']

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

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id',
        'invoice_id.company_id', 'invoice_id.date_invoice', 'invoice_id.date',
        'discount2', 'discount3')
    def _compute_price(self):
        if self.discount2 or self.discount3:
            currency = self.invoice_id and self.invoice_id.currency_id or None
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            price *= 1 - (self.discount2 or 0.0) / 100.0
            price *= 1 - (self.discount3 or 0.0) / 100.0

            taxes = False
            if self.invoice_line_tax_ids:
                taxes = self.invoice_line_tax_ids.\
                    compute_all(price, currency, self.quantity,
                                product=self.product_id,
                                partner=self.invoice_id.partner_id)
            self.price_subtotal = \
                price_subtotal_signed = taxes['total_excluded'] \
                if taxes else self.quantity * price
            if self.invoice_id.currency_id and self.invoice_id.company_id and \
                    self.invoice_id.currency_id != \
                    self.invoice_id.company_id.currency_id:
                price_subtotal_signed = self.invoice_id.currency_id.\
                    with_context(date=self.invoice_id.\
                                 _get_currency_rate_date()).\
                                 compute(price_subtotal_signed,
                                        self.invoice_id.company_id.currency_id)
            sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
            self.price_subtotal_signed = price_subtotal_signed * sign
        else:
            super(AccountInvoiceLine, self)._compute_price()
