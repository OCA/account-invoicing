# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# © 2017 Odoo SA <https://www.odoo.com>
# © 2017 OCA <https://odoo-community.org>
# License LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from openerp import api, exceptions, fields, models
from openerp.tools.translate import _
import json
from openerp.tools.float_utils import float_is_zero
import logging

logging.basicConfig(level=logging.DEBUG)
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _compute_get_outstanding_info_JSON(self):
        """
        Get information for the outstanding payments and return it to the
        widget. This function has been re-used from 9.0.
        @attention: Source in
                    https://github.com/OCA/OCB/blob/9.0/addons/
                    account/models/account_invoice.py#L110
        @author:    Authors credited at README.rst
        """
        for record in self:
            record.outstanding_credits_debits_widget = json.dumps(False)
            if record.state == 'open':
                domain = [('account_id', '=', record.account_id.id),
                          ('partner_id', '=', self.env['res.partner'].
                           _find_accounting_partner(record.partner_id).id),
                          ('reconcile_ref', '=', False)]
                if record.type in ('out_invoice', 'in_refund'):
                    domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                    type_payment = _('Outstanding credits')
                else:
                    domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                    type_payment = _('Outstanding debits')
                info = {'title': '', 'outstanding': True, 'content': [],
                        'invoice_id': record.id}
                lines = self.env['account.move.line'].search(domain)
                currency_id = record.currency_id
                if len(lines) != 0:
                    for line in lines:
                        if line.currency_id and line.currency_id == \
                                record.currency_id:
                            amount_to_show = abs(line.amount_residual_currency)
                        else:
                            amount_to_show = line.company_id.currency_id. \
                                with_context(date=line.date).compute(abs(
                                    line.amount_residual), record.currency_id)
                        if float_is_zero(amount_to_show,
                                         precision_rounding=record.
                                         currency_id.rounding):
                            continue
                        info['content'].append({
                            'journal_name': line.ref or line.move_id.name,
                            'amount': amount_to_show,
                            'currency': currency_id.symbol,
                            'id': line.id,
                            'position': currency_id.position,
                            'digits': [69, record.currency_id.accuracy],
                        })
                    info['title'] = type_payment
                    record.outstanding_credits_debits_widget = json.dumps(info)
                    record.has_outstanding = True

    outstanding_credits_debits_widget = fields.Text(
        compute='_compute_get_outstanding_info_JSON')
    has_outstanding = fields.Boolean(
        compute='_compute_get_outstanding_info_JSON')

    @api.multi
    @api.depends('payment_ids.amount_residual')
    def _compute_get_payment_info_JSON(self):
        """
        Returns the payment info for the invoice to the widget
        @attention: Source in
                    https://github.com/OCA/OCB/blob/9.0/addons/
                    account/models/account_invoice.py#L146
        @author:    Authors credited at README.rst
        """
        for record in self:
            record.payments_widget = json.dumps(False)
            if record.payment_ids:
                info = {'title': _('Less Payment'), 'outstanding': False,
                        'content': []}
                currency_id = record.currency_id
                for payment in record.payment_ids:
                    if record.type in ('out_invoice', 'in_refund'):
                        amount = payment.credit
                    elif record.type in ('in_invoice', 'out_refund'):
                        amount = payment.debit
                    if float_is_zero(amount,
                                     precision_rounding=record.currency_id.
                                     rounding):
                        continue
                    payment_ref = payment.move_id.name
                    if payment.move_id.ref:
                        payment_ref += ' (' + payment.move_id.ref + ')'
                    info['content'].append({
                        'name': payment.name,
                        'journal_name': payment.journal_id.name,
                        'amount': amount,
                        'currency': currency_id.symbol,
                        'digits': [69, currency_id.accuracy],
                        'position': currency_id.position,
                        'date': payment.date,
                        'payment_id': payment.id,
                        'move_id': payment.move_id.id,
                        'ref': payment_ref,
                    })
                record.payments_widget = json.dumps(info)

    payments_widget = fields.Text(compute='_compute_get_payment_info_JSON')

    @api.multi
    def register_payment(self, payment_line, writeoff_acc_id=False,
                         writeoff_journal_id=False):
        """
        @attention: Source in
                    https://github.com/OCA/OCB/blob/9.0/addons/
                    account/models/account_invoice.py#L596
        @author:    Authors credited in README.rst
        """
        line_to_reconcile = self.env['account.move.line']
        for inv in self:
            line_to_reconcile += inv.move_id.line_id.filtered(
                lambda r: not r.reconcile_ref and r.account_id.type in
                ('payable', 'receivable'))
        ir_values_obj = self.env['ir.values']
        reconciliation_writeoff_account = ir_values_obj.get_default(
            'account.config.settings', 'reconciliation_writeoff_account')
        if not reconciliation_writeoff_account:
            raise exceptions.MissingError(_('''Set the write-off account
            in Settings -> Configuration -> Invoicing -> Write-Off account'''))
        return (line_to_reconcile + payment_line).reconcile(
            writeoff_journal_id=self.journal_id.id,
            writeoff_period_id=self.env['account.period'].find().id,
            writeoff_acc_id=reconciliation_writeoff_account)

    @api.multi
    def assign_outstanding_credit(self, credit_aml_id):
        """
        @attention: Source in
                    https://github.com/OCA/OCB/blob/9.0/addons/account/
                    models/account_invoice.py#L604
        @author:    Authors credited in README.rst
        """
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        if not credit_aml.currency_id and self.currency_id != \
                self.company_id.currency_id:
            credit_aml.with_context(allow_amount_currency=True).write({
                'amount_currency': self.company_id.currency_id.with_context(
                    date=credit_aml.date).compute(credit_aml.balance,
                                                  self.currency_id),
                'currency_id': self.currency_id.id})
        return self.register_payment(credit_aml)
