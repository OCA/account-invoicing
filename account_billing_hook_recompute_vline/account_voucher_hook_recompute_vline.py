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

from openerp import models
from openerp.addons.account_voucher.account_voucher import account_voucher


def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
    """
    Returns a dict that contains new values and context

    @param partner_id: latest value from user input for field partner_id
    @param args: other arguments
    @param context: context arguments, like lang, time zone

    @return: Returns a dict which contains new values, and context
    """
    def _remove_noise_in_o2m():
        """if the line is partially reconciled, then we must pay attention to display it only once and
            in the good o2m.
            This function returns True if the line is considered as noise and should not be displayed
        """
        if line.reconcile_partial_id:
            if currency_id == line.currency_id.id:
                if line.amount_residual_currency <= 0:
                    return True
            else:
                if line.amount_residual <= 0:
                    return True
        return False

    if context is None:
        context = {}
    context_multi_currency = context.copy()

    currency_pool = self.pool.get('res.currency')
    move_line_pool = self.pool.get('account.move.line')
    partner_pool = self.pool.get('res.partner')
    journal_pool = self.pool.get('account.journal')
    line_pool = self.pool.get('account.voucher.line')

    #set default values
    default = {
        'value': {'line_dr_ids': [], 'line_cr_ids': [], 'pre_line': False},
    }

    # drop existing lines
    line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])])
    for line in line_pool.browse(cr, uid, line_ids, context=context):
        if line.type == 'cr':
            default['value']['line_cr_ids'].append((2, line.id))
        else:
            default['value']['line_dr_ids'].append((2, line.id))

    if not partner_id or not journal_id:
        return default

    journal = journal_pool.browse(cr, uid, journal_id, context=context)
    partner = partner_pool.browse(cr, uid, partner_id, context=context)
    currency_id = currency_id or journal.company_id.currency_id.id

    total_credit = 0.0
    total_debit = 0.0
    account_type = None
    if context.get('account_id'):
        account_type = self.pool['account.account'].browse(cr, uid, context['account_id'], context=context).type
    if ttype == 'payment':
        if not account_type:
            account_type = 'payable'
        total_debit = price or 0.0
    else:
        total_credit = price or 0.0
        if not account_type:
            account_type = 'receivable'

    if not context.get('move_line_ids', False):
        ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
    else:
        ids = context['move_line_ids']
    invoice_id = context.get('invoice_id', False)
    company_currency = journal.company_id.currency_id.id
    move_lines_found = []

    #order the lines by most old first
    ids.reverse()
    account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

    # HOOK
    account_move_lines = self.finalize_voucher_move_lines(
        cr, uid, ids,
        account_move_lines,
        partner_id, journal_id, price,
        currency_id, ttype, date,
        context=context
    )
    # --

    #compute the total debit/credit and look for a matching open amount or invoice
    for line in account_move_lines:
        if _remove_noise_in_o2m():
            continue

        if invoice_id:
            if line.invoice.id == invoice_id:
                #if the invoice linked to the voucher line is equal to the invoice_id in context
                #then we assign the amount on that line, whatever the other voucher lines
                move_lines_found.append(line.id)
        elif currency_id == company_currency:
            #otherwise treatments is the same but with other field names
            if line.amount_residual == price:
                #if the amount residual is equal the amount voucher, we assign it to that voucher
                #line, whatever the other voucher lines
                move_lines_found.append(line.id)
                break
            #otherwise we will split the voucher amount on each line (by most old first)
            total_credit += line.credit or 0.0
            total_debit += line.debit or 0.0
        elif currency_id == line.currency_id.id:
            if line.amount_residual_currency == price:
                move_lines_found.append(line.id)
                break
            total_credit += line.credit and line.amount_currency or 0.0
            total_debit += line.debit and line.amount_currency or 0.0

    remaining_amount = price
    #voucher line creation
    for line in account_move_lines:

        if _remove_noise_in_o2m():
            continue

        if line.currency_id and currency_id == line.currency_id.id:
            amount_original = abs(line.amount_currency)
            amount_unreconciled = abs(line.amount_residual_currency)
        else:
            #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
            amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
            amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual), context=context_multi_currency)
        line_currency_id = line.currency_id and line.currency_id.id or company_currency
        rs = {
            'name':line.move_id.name,
            'type': line.credit and 'dr' or 'cr',
            'move_line_id':line.id,
            'account_id':line.account_id.id,
            'amount_original': amount_original,
            'amount': (line.id in move_lines_found) and min(abs(remaining_amount), amount_unreconciled) or 0.0,
            'date_original':line.date,
            'date_due':line.date_maturity,
            'amount_unreconciled': amount_unreconciled,
            'currency_id': line_currency_id,
        }
        remaining_amount -= rs['amount']
        #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
        #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
        if not move_lines_found:
            if currency_id == line_currency_id:
                if line.credit:
                    amount = min(amount_unreconciled, abs(total_debit))
                    rs['amount'] = amount
                    total_debit -= amount
                else:
                    amount = min(amount_unreconciled, abs(total_credit))
                    rs['amount'] = amount
                    total_credit -= amount

        if rs['amount_unreconciled'] == rs['amount']:
            rs['reconcile'] = True

        if rs['type'] == 'cr':
            default['value']['line_cr_ids'].append(rs)
        else:
            default['value']['line_dr_ids'].append(rs)

        if len(default['value']['line_cr_ids']) > 0:
            default['value']['pre_line'] = 1
        elif len(default['value']['line_dr_ids']) > 0:
            default['value']['pre_line'] = 1
        default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
    return default


class AccountVoucherHookRecomputeVLine(models.AbstractModel):

    _name = 'account.voucher.hook.recompute.vline'
    _description = 'Provide hook point for recompute voucher line function'

    def _register_hook(self, cr):
        account_voucher.recompute_voucher_lines = recompute_voucher_lines
        return super(AccountVoucherHookRecomputeVLine, self)._register_hook(cr)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
