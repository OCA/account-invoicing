# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, exceptions, fields, models
from openerp.tools.translate import _
import json
from openerp.tools.float_utils import float_is_zero


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def _get_outstanding_info_JSON(self):
        self.outstanding_credits_debits_widget = json.dumps(False)
        if self.state == 'open':
            domain = [('account_id', '=', self.account_id.id),
                      ('partner_id', '=', self.env['res.partner'].
                       _find_accounting_partner(self.partner_id).id),
                      ('reconcile_ref', '=', False)]
            if self.type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [],
                    'invoice_id': self.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = self.currency_id
            if len(lines) != 0:
                for line in lines:
                    if line.currency_id and line.currency_id == \
                            self.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        amount_to_show = line.company_id.currency_id. \
                            with_context(date=line.date).compute(abs(
                                line.amount_residual), self.currency_id)
                    if float_is_zero(amount_to_show, precision_rounding=self.
                                     currency_id.rounding):
                        continue
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, self.currency_id.accuracy],
                    })
                info['title'] = type_payment
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True

    outstanding_credits_debits_widget = fields.Text(
        compute='_get_outstanding_info_JSON')
    has_outstanding = fields.Boolean(compute='_get_outstanding_info_JSON')

    @api.one
    @api.depends('payment_ids.amount_residual')
    def _get_payment_info_JSON(self):
        '''
        Returns the payment info for the invoice to the widget
        '''
        self.payments_widget = json.dumps(False)
        if self.payment_ids:
            info = {'title': _('Less Payment'), 'outstanding': False,
                    'content': []}
            currency_id = self.currency_id
            for payment in self.payment_ids:
                if self.type in ('out_invoice', 'in_refund'):
                    amount = payment.credit
                elif self.type in ('in_invoice', 'out_refund'):
                    amount = payment.debit
                if float_is_zero(amount,
                                 precision_rounding=self.currency_id.rounding):
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
            self.payments_widget = json.dumps(info)

    payments_widget = fields.Text(compute='_get_payment_info_JSON')

    @api.multi
    def register_payment(self, payment_line, writeoff_acc_id=False,
                         writeoff_journal_id=False):
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

    @api.v7
    def assign_outstanding_credit(self, cr, uid, _id, credit_aml_id,
                                  context=None):
        credit_aml = self.pool.get('account.move.line').browse(
            cr, uid, credit_aml_id, context=context)
        inv = self.browse(cr, uid, _id, context=context)
        if not credit_aml.currency_id and inv.currency_id != \
                inv.company_id.currency_id:
            credit_aml.with_context(allow_amount_currency=True).write({
                'amount_currency': inv.company_id.currency_id.with_context(
                    date=credit_aml.date).compute(credit_aml.balance,
                                                  inv.currency_id),
                'currency_id': inv.currency_id.id})
        return inv.register_payment(credit_aml)
