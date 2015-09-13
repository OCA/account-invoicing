# -*- coding: utf-8 -*-
#
#    Author: Kitti Upariphutthiphong
#    Copyright 2014-2015 Ecosoft Co., Ltd.
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
#

import time

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
import openerp.addons.decimal_precision as dp


class AccountBilling(models.Model):

    # Private attributes
    _name = 'account.billing'
    _description = 'Account Billing'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    # Fields declaration
    number = fields.Char(
        string='Number',
        size=32,
        readonly=True,
        copy=False,)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        change_default=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self._context.get('partner_id', False))
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self._context.get('company_id',
                                               self.env.user.company_id.id))
    date = fields.Date(
        string='Date',
        select=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: time.strftime('%Y-%m-%d'),
        help="Effective date for accounting entries")
    line_cr_ids = fields.One2many(
        'account.billing.line',
        'billing_id',
        string='Credits',
        context={'default_type': 'cr'},
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False)
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        default=lambda self: self._default_period(),
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    narration = fields.Text(
        string='Notes',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self._context.get('narration', False))
    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('billed', 'Billed')],
        string='Status',
        readonly=True,
        default='draft',
        help="""* The 'Draft' status is used when a user is encoding a new and
            unconfirmed billing.
            \n* The 'Billed' status is used when user create billing,
            a billing number is generated
            \n* The 'Cancelled' status is used when user cancel billing.""")
    reference = fields.Char(
        string='Ref #',
        size=64,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Transaction reference number.",
        default=lambda self: self._context.get('reference', False),
        copy=False)
    billing_amount = fields.Float(
        string='Billing Amount',
        compute='_compute_billing_amount',
        readonly=True,
        store=True,
        help="""Computed as the difference between the amount stated in the
            billing and the sum of allocation on the billing lines.""")
    payment_id = fields.Many2one(
        'account.voucher',
        string='Payment Ref#',
        required=False,
        readonly=True)
    name = fields.Char(
        string='Memo',
        size=256,
        readonly=True,
        states={'draft': [('readonly', False)]})

    @api.model
    def _default_period(self):
        return self.env['account.period'].find()

    @api.multi
    def name_get(self):
        result = []
        for billing in self:
            result.append((billing.id, (billing.number or 'N/A')))
        return result

    @api.one
    @api.depends('line_cr_ids')
    def _compute_billing_amount(self):
        credit = 0.0
        for l in self.line_cr_ids:
            credit += l.amount
        currency = self.currency_id or self.company_id.currency_id
        self.billing_amount = currency.round(credit)

    @api.model
    def create(self, vals):
        billing = super(AccountBilling, self).create(vals)
        billing.create_send_note()
        return billing

    @api.multi
    def onchange_partner_id(self, company_id,
                            partner_id, currency_id, date):
        ctx = self._context.copy()
        ctx.update(
            {'billing_date_condition': ['|',
                                        ('date_maturity', '=', False),
                                        ('date_maturity', '<=', date)]}
        )
        if not currency_id:
            return {'value': {'line_cr_ids': []}}
        res = self.with_context(ctx).recompute_billing_lines(
            company_id, partner_id, currency_id, date)
        return res

    def recompute_billing_lines(self, cr, uid, ids, company_id,
                                partner_id, currency_id, date, context=None):

        def _remove_noise_in_o2m():
            if line.reconcile_partial_id:
                sign = 1
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency * sign <= 0:
                        return True
                else:
                    if line.amount_residual * sign <= 0:
                        return True
            return False

        if context is None:
            context = {}
        billing_date_condition = context.get('billing_date_condition', [])
        move_line_pool = self.pool.get('account.move.line')
        default = {'value': {'line_cr_ids': []}}

        if not partner_id or not currency_id:
            return default

        account_type = ('payable', 'receivable')
        # if currency_id = company currency, it value could be false.
        company = self.pool.get('res.company').browse(cr, uid, company_id)
        if company and company.currency_id.id == currency_id:
            currency_domain = [('currency_id', 'in', (False, currency_id))]
        else:
            currency_domain = [('currency_id', '=', currency_id)]

        ids = move_line_pool.search(cr, uid, [
            ('state', '=', 'valid'),
            ('account_id.type', 'in', account_type),
            ('reconcile_id', '=', False),
            ('partner_id', '=', partner_id)
        ] + currency_domain + billing_date_condition, context=context)

        # Order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids,
                                                   context=context)
        # Billing line creation
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue
            amount_original = 0.0
            if line.amount_currency:
                amount_original = line.amount_currency
            else:
                amount_original = line.debit and line.debit or line.credit
            amount_unreconciled = abs(line.amount_residual_currency)
            amount = amount_unreconciled
            rs = {
                'move_line_id': line.id,
                'type': line.credit and 'dr' or 'cr',
                'reference': line.invoice.reference,
                'amount_original': amount_original,
                'amount': amount,
                'date_original': line.date,
                'date_due': line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': currency_id,
            }
            # Negate DR records
            if rs['type'] == 'dr':
                rs['amount_original'] = - rs['amount_original']
                rs['amount'] = - rs['amount']
                rs['amount_unreconciled'] = - rs['amount_unreconciled']
            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True
            else:
                rs['reconcile'] = False
            default['value']['line_cr_ids'].append(rs)
        line_cr_ids = default['value']['line_cr_ids']
        billing_amount = sum([line['amount'] for line in line_cr_ids])
        default['value']['billing_amount'] = billing_amount
        return default

    @api.multi
    def onchange_date(self, company_id, date, partner_id, currency_id):
        res = {'value': {}}
        # Set the period of the billing
        period_pool = self.env['account.period']
        pids = period_pool.find(dt=date)
        if pids:
            res['value'].update({'period_id': pids[0]})
        res2 = self.onchange_partner_id(company_id, partner_id,
                                        currency_id, date)
        for key in res2.keys():
            res[key].update(res2[key])
        return res

    @api.multi
    def onchange_currency_id(self, company_id,
                             currency_id, partner_id, date):
        vals = {'value': {}}
        vals['value'].update({'currency_id': currency_id})
        res = self.onchange_partner_id(company_id, partner_id,
                                       currency_id, date)
        for key in res.keys():
            vals[key].update(res[key])
        return vals

    @api.multi
    def validate_billing(self):
        self.write({'state': 'billed'})
        self.write({'number': self.env['ir.sequence'].get('account.billing')})
        self.message_post(body=_('Billing is billed.'))

    @api.multi
    def action_cancel_draft(self):
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        self.message_post(body=_('Billing is reset to draft'))
        return True

    @api.multi
    def cancel_billing(self):
        self.write({'state': 'cancel'})
        self.message_post(body=_('Billing is cancelled'))
        return True

    @api.multi
    def unlink(self):
        for billing in self:
            if billing.state not in ('draft', 'cancel'):
                raise except_orm(
                    _('Invalid Action!'),
                    _('Cannot delete billing(s) which are already billed.'))
        return super(AccountBilling, self).unlink()

    _document_type = {
        'payment': 'Supplier Billing',
        'receipt': 'Customer Billing',
        False: 'Payment',
    }

    @api.multi
    def create_send_note(self):
        message = "Billing Document <b>created</b>."
        self.message_post(body=message,
                          subtype="account_billing.mt_billing")


class AccountBillingLine(models.Model):

    _name = 'account.billing.line'
    _description = 'Billing Lines'
    _order = 'move_line_id'

    billing_id = fields.Many2one(
        'account.billing',
        string='billing',
        required=1,
        ondelete='cascade')
    name = fields.Char(
        string='Description',
        size=256)
    reference = fields.Char(
        string='Invoice Reference',
        size=64,
        help="The partner reference of this invoice.")
    partner_id = fields.Many2one(
        'res.partner',
        related='billing_id.partner_id',
        string='Partner')
    untax_amount = fields.Float(string='Untaxed Amount')
    amount = fields.Float(
        string='Amount',
        digits_compute=dp.get_precision('Account'))
    reconcile = fields.Boolean(string='Full Reconcile')
    type = fields.Selection(
        [('dr', 'Debit'),
         ('cr', 'Credit')],
        string='Dr/Cr')
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account')
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item')
    date_original = fields.Date(
        related='move_line_id.date',
        string='Date',
        readonly=1)
    date_due = fields.Date(
        related='move_line_id.date_maturity',
        string='Due Date',
        readonly=1)
    amount_original = fields.Float(
        string='Original Amount',
        digits_compute=dp.get_precision('Account'),
        store=True)
    amount_unreconciled = fields.Float(
        string='Open Balance',
        digits_compute=dp.get_precision('Account'),
        store=True)

    @api.multi
    def onchange_reconcile(self, reconcile, amount, amount_unreconciled):
        vals = {'amount': 0.0}
        if reconcile:
            vals = {'amount': amount_unreconciled}
        return {'value': vals}

    @api.multi
    def onchange_amount(self, reconcile, amount, amount_unreconciled):
        vals = {}
        if amount == amount_unreconciled:
            vals = {'reconcile': True}
        else:
            vals = {'reconcile': False, 'amount': 0.0}
        return {'value': vals}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
