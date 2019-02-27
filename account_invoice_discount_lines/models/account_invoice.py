# coding: utf-8
# Copyright 2017 Opener B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def copy(self, default=None):
        invoice = super(AccountInvoice, self).copy(default)
        invoice.reset_discount()
        return invoice

    @api.multi
    def reset_discount(self):
        for invoice in self:
            discount_lines = invoice.invoice_line.filtered('discount_line')
            for line in invoice.invoice_line.filtered('discount_real'):
                line.discount = line.discount_real
            if discount_lines:
                discount_lines.unlink()
                invoice.button_reset_taxes()

    @api.multi
    @api.returns('self')
    def refund(self, date=None, period_id=None,
               description=None, journal_id=None):
        invoices = super(AccountInvoice, self).refund(
            date=date, period_id=period_id, description=description,
            journal_id=journal_id)
        invoices.reset_discount()
        return invoices

    @api.multi
    def action_cancel_draft(self):
        self.reset_discount()
        return super(AccountInvoice, self).action_cancel_draft()

    @api.multi
    def action_move_create(self):
        """ Transfer discount percentages to discount lines """
        for invoice in self:
            discount_map = {}
            for line in invoice.invoice_line:
                if line.discount:
                    line.discount_real = line.discount
                    line.discount = 0
                    product = line.get_discount_product().with_context(
                        lang=invoice.partner_id.lang)
                    discount_map.setdefault(
                        (product, tuple(line.invoice_line_tax_id)), []
                    ).append(line)
            for (product, taxes), lines in discount_map.items():
                currency = (invoice.journal_id.currency or
                            invoice.company_id.currency_id)
                price_unit = currency.round(
                    -1 * sum((line.discount_real / 100) * line.quantity *
                             line.price_unit
                             for line in lines))
                discount_line = lines[0].copy(default={
                    'product_id': product.id,
                    'price_unit': price_unit,
                    'uos_id': product.uom_id.id,
                    'discount': 0.0,
                    'quantity': 1,
                    'discount_line': True,
                    'discount_real': 0,
                })
                values = self.env['account.invoice.line'].product_id_change(
                    product=product.id, uom_id=product.uom_id.id, qty=1,
                    type=invoice.type,
                    partner_id=invoice.partner_id.id,
                    fposition_id=invoice.fiscal_position.id,
                    price_unit=price_unit,
                    company_id=invoice.company_id.id)['value']
                values.pop('invoice_line_tax_id', False)
                values.pop('price_unit', False)
                discount_line.write(values)

            if discount_map:
                # Always recompute taxes, to cover the case that there is no
                # tax ledger account configured or small rounding differences
                # with included taxes.
                invoice.button_reset_taxes()

        return super(AccountInvoice, self).action_move_create()
