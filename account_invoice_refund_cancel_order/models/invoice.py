# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from datetime import date

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def refund_cancel_order(self, order_name):
        payment_method_obj = self.env['account.payment.method']
        payment_obj = self.env['account.payment']

        self.ensure_one()
        if self.state not in ('open', 'paid'):
            return False

        today = date.today()
        today_str = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
        description = _('cancel sale order %s') % order_name
        refund = self.refund(
            today_str, False, description,
            self.journal_id.id)
        subject = _("Invoice refund")
        refund.message_post(body=description, subject=subject)
        if self.state == 'open':
            movelines = self.move_id.line_ids
            to_reconcile_ids = {}
            to_reconcile_lines = self.env['account.move.line']
            for line in movelines:
                if line.account_id.id == self.account_id.id:
                    to_reconcile_lines += line
                    to_reconcile_ids.setdefault(
                        line.account_id.id, []).append(line.id)
                if line.reconciled:
                    line.remove_move_reconcile()
        # validate refund invoice:
        refund.action_invoice_open()

        if self.state == 'paid':
            # automatic pay:
            payment_method = payment_method_obj.search([
                ('code', '=', 'manual'),
                ('payment_type', '=', 'inbound'),
            ])
            payment = payment_obj.create({
                'journal_id': refund.journal_id.id,
                'payment_date': today_str,
                'amount': refund.amount_total,
                'communication': description,
                'payment_method_id': payment_method.id,
                'payment_type': 'outbound',
                'partner_type': 'customer',
                'partner_id': refund.partner_id.id,
                'currency_id': refund.currency_id.id,
                'invoice_ids': [(6, False, [refund.id])],
                'company_id': refund.company_id.id,
            })
            payment.post()
        else:
            # reconcile invoices each other:
            for tmpline in refund.move_id.line_ids:
                if tmpline.account_id.id == self.account_id.id:
                    to_reconcile_lines += tmpline
            to_reconcile_lines.filtered(lambda l: not l.reconciled).reconcile()

        return True
