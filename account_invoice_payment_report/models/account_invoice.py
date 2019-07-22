# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo import models, fields
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    # Backport of odoo v12.0 method
    def _get_payments_vals(self):

        self.ensure_one()
        if not self.payment_move_line_ids:
            return []
        payment_vals = []
        currency_id = self.currency_id
        for payment in self.payment_move_line_ids:
            payment_currency_id = False
            if self.type in ('out_invoice', 'in_refund'):
                amount = sum(
                    [
                        p.amount
                        for p in payment.matched_debit_ids
                        if p.debit_move_id in self.move_id.line_ids
                    ]
                )
                amount_currency = sum(
                    [
                        p.amount_currency
                        for p in payment.matched_debit_ids
                        if p.debit_move_id in self.move_id.line_ids
                    ]
                )
                if payment.matched_debit_ids:
                    payment_currency_id = (
                        all(
                            [
                                p.currency_id
                                == payment.matched_debit_ids[0].currency_id
                                for p in payment.matched_debit_ids
                            ]
                        )
                        and payment.matched_debit_ids[0].currency_id
                        or False
                    )
            elif self.type in ('in_invoice', 'out_refund'):
                amount = sum(
                    [
                        p.amount
                        for p in payment.matched_credit_ids
                        if p.credit_move_id in self.move_id.line_ids
                    ]
                )
                amount_currency = sum(
                    [
                        p.amount_currency
                        for p in payment.matched_credit_ids
                        if p.credit_move_id in self.move_id.line_ids
                    ]
                )
                if payment.matched_credit_ids:
                    payment_currency_id = (
                        all(
                            [
                                p.currency_id
                                == payment.matched_credit_ids[0].currency_id
                                for p in payment.matched_credit_ids
                            ]
                        )
                        and payment.matched_credit_ids[0].currency_id
                        or False
                    )
            # get the payment value in invoice currency
            if payment_currency_id and payment_currency_id == self.currency_id:
                amount_to_show = amount_currency
            else:
                currency = payment.company_id.currency_id
                ctx_date = self.date or fields.Date.today()
                amount_to_show = currency.with_context(date=ctx_date).compute(
                    amount, self.currency_id
                )
            if float_is_zero(
                amount_to_show, precision_rounding=self.currency_id.rounding
            ):
                continue
            payment_ref = payment.move_id.name
            if payment.move_id.ref:
                payment_ref += ' (' + payment.move_id.ref + ')'
            payment_vals.append(
                {
                    'name': payment.name,
                    'journal_name': payment.journal_id.name,
                    'amount': amount_to_show,
                    'currency': currency_id.symbol,
                    'digits': [69, currency_id.decimal_places],
                    'position': currency_id.position,
                    'date': payment.date,
                    'payment_id': payment.id,
                    'account_payment_id': payment.payment_id.id,
                    'invoice_id': payment.invoice_id.id,
                    'move_id': payment.move_id.id,
                    'ref': payment_ref,
                }
            )
        return payment_vals
