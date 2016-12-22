# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.tools.float_utils import float_round, float_compare
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _swedish_add_invoice_line(self, invoice, rounded_total, delta):
        """ Create a invoice_line with the diff of rounding """

        invoice_line_obj = self.env['account.invoice.line']
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')

        company = invoice.company_id
        if not invoice.global_round_line_id.id:
            new_invoice_line = {
                'name': _('Rounding'),
                'price_unit': -delta,
                'account_id': company.tax_calculation_rounding_account_id.id,
                'invoice_id': invoice.id,
                'is_rounding': True,
            }
            invoice_line_obj.create(new_invoice_line)
        elif float_compare(invoice.global_round_line_id.price_unit, -delta,
                           precision_digits=prec) != 0:
            invoice_line_obj.write(invoice.global_round_line_id.id,
                                   {'price_unit': -delta})

        amount_untaxed = float_round(invoice.amount_untaxed - delta,
                                     precision_digits=prec)
        return {'amount_total': rounded_total,
                'amount_untaxed': amount_untaxed}

    @staticmethod
    def _all_invoice_tax_line_computed(invoice):
        """ Check if all taxes have been computed on invoice lines
        :return boolean True if all tax were computed
        """
        tax_ids = set()
        for line in invoice.invoice_line_ids:
            # invoice_line_tax_id is a many2many if you wonder about it
            for tax in line.invoice_line_tax_ids:
                if not tax.price_include:
                    tax_ids.add(tax.id)
        computed_tax_ids = [tax.id for tax in invoice.tax_line_ids]
        return len(tax_ids) == len(computed_tax_ids)

    @api.model
    def _swedish_round_globally(self, invoice, rounded_total, delta):
        """ Add the diff to the biggest tax line
        This ajustment must be done only after all tax are computed
        """
        # Here we identify that all taxe lines have been computed
        if not self._all_invoice_tax_line_computed(invoice):
            return {}

        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        inv_tax_obj = self.env['account.invoice.tax']

        ajust_line = None
        for tax_line in invoice.tax_line:
            if not ajust_line or tax_line.amount > ajust_line.amount:
                ajust_line = tax_line
        if ajust_line:
            amount = ajust_line.amount - delta
            vals = inv_tax_obj.amount_change(
                [ajust_line.id], amount, currency_id=invoice.currency_id.id,
                company_id=invoice.company_id.id,
                date_invoice=invoice.date_invoice)['value']
            ajust_line.write({'amount': amount,
                              'tax_amount': vals['tax_amount']})

            amount_tax = float_round(invoice.amount_tax - delta,
                                     precision_digits=prec)
            return {'amount_total': rounded_total,
                    'amount_tax': amount_tax}
        return {}

    @api.model
    def _compute_swedish_rounding(self, invoice):
        """
        Depending on the method defined, we add an invoice line or adapt the
        tax lines to have a rounded total amount on the invoice
        :param invoice: invoice browse record
        :return dict: updated values for _amount_all
        """
        obj_precision = self.env['decimal.precision']

        # avoid recusivity
        if 'swedish_write' in self.env.context:
            return {}

        company = invoice.company_id
        round_method = company.tax_calculation_rounding_method

        if round_method[:7] != 'swedish':
            return {}

        prec = obj_precision.precision_get('Account')
        rounding_prec = company.tax_calculation_rounding
        if rounding_prec <= 0.00:
            return {}
        rounded_total = float_round(invoice.amount_total,
                                    precision_rounding=rounding_prec)

        if float_compare(rounded_total, invoice.amount_total,
                         precision_digits=prec) == 0:
            return {}

        # To avoid recursivity as we need to write on invoice or
        # on objects triggering computation of _amount_all
        ctx = self.env.context.copy()
        ctx['swedish_write'] = True

        delta = float_round(invoice.amount_total - rounded_total,
                            precision_digits=prec)
        if round_method == 'swedish_add_invoice_line':
            return self._swedish_add_invoice_line(invoice, rounded_total,
                                                  delta)
        elif round_method == 'swedish_round_globally':
            return self._swedish_round_globally(invoice, rounded_total,
                                                delta)
        return {}

    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount')
    def _compute_amount(self):
        """ Add swedish rounding computing
        Makes sure invoice line for rounding is not computed in totals
        """
        super(AccountInvoice, self)._compute_amount()
        for invoice in self:
            if invoice.type in ('out_invoice', 'out_refund'):
                if invoice.global_round_line_id.id:
                    line = invoice.global_round_line_id
                    if line:
                        invoice.amount_untaxed -= line.price_subtotal
                invoice.amount_total = invoice.amount_tax + invoice.\
                    amount_untaxed
                swedish_rounding = self._compute_swedish_rounding(invoice)
                if swedish_rounding:
                    invoice.amount_total = swedish_rounding['amount_total']
                    if 'amount_tax' in swedish_rounding:
                        invoice.amount_tax = swedish_rounding['amount_tax']
                    elif 'amount_untaxed' in swedish_rounding:
                        invoice.amount_untaxed = (
                            swedish_rounding['amount_untaxed'])

    def _get_rounding_invoice_line_id(self):
        for invoice in self:
            lines = self.env['account.invoice.line'].search(
                [('invoice_id', '=', invoice.id),
                 ('is_rounding', '=', True)])
            invoice.global_round_line_id = lines

    global_round_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice Line for total rounding',
        compute=_get_rounding_invoice_line_id,
        readonly=True)
    amount_untaxed = fields.Float(
        digits=dp.get_precision('Account'),
        string='Subtotal',
        track_visibility='always',
        compute=_compute_amount,
        store=True)
    amount_tax = fields.Float(
        compute=_compute_amount,
        digits=dp.get_precision('Account'),
        string='Tax',
        store=True)
    amount_total = fields.Float(
        compute=_compute_amount,
        digits=dp.get_precision('Account'),
        string='Total',
        store=True)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    is_rounding = fields.Boolean('Rounding Line')


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def compute_inv(self, taxes, price_unit, quantity, product=None,
                    partner=None, precision=None):
        """
        Using swedish rounding we want to keep standard global precision
        so we add precision to do global computation
        """
        if taxes and taxes[0].company_id.tax_calculation_rounding_method[:7] \
                == 'swedish':
            if not precision:
                precision = self.env['decimal.precision'].precision_get(
                    'Account')
            precision += 5
        return super(AccountTax, self).compute_inv(taxes, price_unit,
                                                   quantity,
                                                   product=product,
                                                   partner=partner,
                                                   precision=precision)

    @api.model
    def _compute(self, taxes, price_unit, quantity, product=None,
                 partner=None, precision=None):
        """Using swedish rounding we want to keep standard global precision
        so we add precision to do global computation
        """
        if taxes and taxes[0].company_id.tax_calculation_rounding_method[:7] \
                == 'swedish':
            if not precision:
                precision = \
                    self.env['decimal.precision'].precision_get('Account')
            precision += 5
        return super(AccountTax, self)._compute(taxes, price_unit, quantity,
                                                product=product,
                                                partner=partner,
                                                precision=precision)
