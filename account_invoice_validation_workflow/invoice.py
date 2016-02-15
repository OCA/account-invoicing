# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-Guillaume
#    Copyright 2010-2015 Camptocamp SA
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
from openerp import models, fields, api, exceptions
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval
from openerp import netsvc


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_to_valid(self):
        """Check if analytic account of each lines is not closed"""
        str_error_lines = ""
        errors = False
        for inv in self:
            for line in inv.invoice_line:
                if line.account_analytic_id and \
                        line.account_analytic_id.state in ['close',
                                                           'cancelled']:
                    str_error_lines += "\n- %s" % line.name
                    errors = True
            if errors:
                raise exceptions.Warning(
                    _("You are trying to validate invoice lines linked to a "
                      "closed or cancelled Analytic Account.\n\n"
                      "Check the following lines:") + str_error_lines)
        self.write({'state': 'to_valid'})
        return True

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('to_send', 'To Send'),
            ('to_valid', 'To Validate'),
            ('proforma2', 'Pro-forma'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Canceled')
        ], 'State', select=True, readonly=True)


class AccountInvoiceRefund(orm.TransientModel):
    _inherit = "account.invoice.refund"

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs
        """
        inv_obj = self.pool['account.invoice']
        reconcile_obj = self.pool['account.move.reconcile']
        account_m_line_obj = self.pool['account.move.line']
        mod_obj = self.pool['ir.model.data']
        act_obj = self.pool['ir.actions.act_window']
        wf_service = netsvc.LocalService('workflow')
        inv_tax_obj = self.pool['account.invoice.tax']
        inv_line_obj = self.pool['account.invoice.line']
        res_users_obj = self.pool['res.users']
        if context is None:
            context = {}
        for form in self.read(cr, uid, ids, context=context):
            created_inv = []
            date = False
            period = False
            description = False
            journal_id = False
            company = res_users_obj.browse(
                cr, uid, uid, context=context).company_id
            if form.get('journal_id', False):
                journal_id = form['journal_id'][0]
            for inv in inv_obj.browse(cr, uid, context.get('active_ids'),
                                      context=context):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise orm.except_orm(
                        _('Error !'),
                        _('Can not %s draft/proforma/cancel invoice.') % mode)
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise orm.except_orm(
                        _('Error !'),
                        _('Can not %s invoice which is already reconciled, '
                          'invoice should be unreconciled first. You can only '
                          'Refund this invoice') % mode)
                if form.get('period'):
                    period = form['period'][0]
                else:
                    period = inv.period_id and inv.period_id.id or False
                if not journal_id:
                    journal_id = inv.journal_id.id
                if form['date']:
                    date = form['date']
                    if not form['period']:
                        cr.execute("select name from ir_model_fields \
                                            where model = 'account.period' \
                                            and name = 'company_id'")
                        result_query = cr.fetchone()
                        if result_query:
                            cr.execute(
                                """select p.id
                                from account_fiscalyear y,
                                    account_period p
                                where y.id=p.fiscalyear_id
                                    and date(%s) between p.date_start
                                    AND p.date_stop and y.company_id = %s
                                limit 1""", (date, company.id,))
                        else:
                            cr.execute(
                                """SELECT id
                                from account_period
                                where date(%s) between date_start AND date_stop
                                limit 1 """, (date,))
                        res = cr.fetchone()
                        if res:
                            period = res[0]
                else:
                    date = inv.date_invoice
                if form['description']:
                    description = form['description']
                else:
                    description = inv.name
                if not period:
                    raise orm.except_orm(_('Data Insufficient !'),
                                         _('No Period found on Invoice!'))
                refund_id = inv_obj.refund(
                    cr, uid, [inv.id], date, period, description, journal_id)
                refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                inv_obj.write(
                    cr, uid, [refund.id],
                    {'date_due': date, 'check_total': inv.check_total})
                inv_obj.button_compute(cr, uid, refund_id)
                created_inv.append(refund_id[0])
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_id
                    to_reconcile_ids = {}
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_ids[line.account_id.id] = [line.id]
                        if type(line.reconcile_id) != orm.orm.browse_null:
                            reconcile_obj.unlink(cr, uid, line.reconcile_id.id)
                    # Specific to c2c need to trigger specific wrkf before
                    # create the refund
                    wf_service.trg_validate(uid, 'account.invoice',
                                            refund.id, 'invoice_to_valid', cr)
                    wf_service.trg_validate(uid, 'account.invoice',
                                            refund.id, 'invoice_to_send', cr)
                    wf_service.trg_validate(uid, 'account.invoice',
                                            refund.id, 'invoice_open', cr)
                    refund = inv_obj.browse(
                        cr, uid, refund_id[0], context=context)
                    for tmpline in refund.move_id.line_id:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_ids[
                                tmpline.account_id.id].append(tmpline.id)
                    for account in to_reconcile_ids:
                        account_m_line_obj.reconcile(
                            cr, uid, to_reconcile_ids[account],
                            writeoff_period_id=period,
                            writeoff_journal_id=inv.journal_id.id,
                            writeoff_acc_id=inv.account_id.id,
                            context={'date_p': date})
                    if mode == 'modify':
                        invoice = inv_obj.read(
                            cr, uid, [inv.id],
                            ['name', 'type', 'number', 'reference',
                             'comment', 'date_due', 'partner_id',
                             'address_contact_id', 'address_invoice_id',
                             'partner_insite', 'partner_contact',
                             'partner_ref', 'payment_term', 'account_id',
                             'currency_id', 'invoice_line', 'tax_line',
                             'journal_id', 'period_id'], context=context)
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.read(
                            cr, uid, invoice['invoice_line'], context=context)
                        invoice_lines = inv_obj._refund_cleanup_lines(
                            cr, uid, invoice_lines)
                        tax_lines = inv_tax_obj.read(
                            cr, uid, invoice['tax_line'], context=context)
                        tax_lines = inv_obj._refund_cleanup_lines(
                            cr, uid, tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': date,
                            'state': 'draft',
                            'number': False,
                            'invoice_line': invoice_lines,
                            'tax_line': tax_lines,
                            'period_id': period,
                            'name': description
                        })
                        for field in ('address_contact_id',
                                      'address_invoice_id', 'partner_id',
                                      'account_id', 'currency_id',
                                      'payment_term', 'journal_id'):
                            invoice[field] = invoice[
                                field] and invoice[field][0]
                        inv_id = inv_obj.create(cr, uid, invoice, {})
                        if inv.payment_term.id:
                            data = inv_obj.onchange_payment_term_date_invoice(
                                cr, uid, [inv_id], inv.payment_term.id, date)
                            if 'value' in data and data['value']:
                                inv_obj.write(cr, uid, [inv_id], data['value'])
                        created_inv.append(inv_id)
            if inv.type in ('out_invoice', 'out_refund'):
                xml_id = 'action_invoice_tree3'
            else:
                xml_id = 'action_invoice_tree4'
            result = mod_obj.get_object_reference(cr, uid, 'account', xml_id)
            id = result and result[1] or False
            result = act_obj.read(cr, uid, id, context=context)
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
