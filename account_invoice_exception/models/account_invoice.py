# -*- coding: utf-8 -*-
# © 2016 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import api, models, fields
from openerp.exceptions import except_orm
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    _order = 'main_exception_id asc, date_invoice desc, number desc'

    main_exception_id = fields.Many2one(
        'account.invoice.exception',
        compute='_get_main_error',
        string='Main Exception',
        store=True
    )
    exception_ids = fields.Many2many(
        'account.invoice.exception',
        'account_invoice_exception_rel',
        'invoice_id',
        'exception_id',
        string='Exceptions'
    )
    ignore_exceptions = fields.Boolean(
        'Ignore Exceptions',
        copy=False
    )

    @api.one
    @api.depends('state', 'exception_ids')
    def _get_main_error(self):
        if self.state == 'draft' and self.exception_ids:
            self.main_exception_id = self.exception_ids[0]
        else:
            self.main_exception_id = False

    @api.model
    def test_all_draft_invoices(self):
        invoice_set = self.search([('state', '=', 'draft')])
        invoice_set.test_exceptions()
        return True

    @api.multi
    def _popup_exceptions(self):
        model_data_model = self.env['ir.model.data']
        wizard_model = self.env['account.invoice.exception.confirm']

        new_context = {'active_id': self.ids[0], 'active_ids': self.ids}
        wizard = wizard_model.with_context(new_context).create({})

        view_id = model_data_model.get_object_reference(
            'account_invoice_exceptions',
            'account_invoice_exception_confirm')[1]

        action = {
            'name': _("Blocked in draft due to exceptions"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.exception.confirm',
            'view_id': [view_id],
            'target': 'new',
            'nodestroy': True,
            'res_id': wizard.id,
        }
        return action

    @api.multi
    def action_button_confirm(self):
        self.ensure_one()
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            return super(AccountInvoice, self).action_button_confirm()

    @api.multi
    def test_exceptions(self):
        """
        Condition method for the workflow from draft to confirm
        """
        if self.detect_exceptions():
            return False
        return True

    @api.multi
    def detect_exceptions(self):
        """returns the list of exception_ids for all the considered invoices

        as a side effect, the invoice's exception_ids column is updated with
        the list of exceptions related to the invoice
        """
        exception_obj = self.env['account.invoice.exception']
        invoice_exceptions = exception_obj.search(
            [('model', '=', 'account.invoice')])
        line_exceptions = exception_obj.search(
            [('model', '=', 'account.invoice.line')])

        all_exception_ids = []
        for invoice in self:
            if invoice.ignore_exceptions:
                continue
            exception_ids = invoice._detect_exceptions(invoice_exceptions,
                                                       line_exceptions)
            invoice.exception_ids = [(6, 0, exception_ids)]
            all_exception_ids += exception_ids
        return all_exception_ids

    @api.model
    def _exception_rule_eval_context(self, obj_name, rec):
        user = self.env['res.users'].browse(self._uid)
        return {obj_name: rec,
                'self': self.pool.get(rec._name),
                'object': rec,
                'obj': rec,
                'pool': self.pool,
                'cr': self._cr,
                'uid': self._uid,
                'user': user,
                'time': time,
                # copy context to prevent side-effects of eval
                'context': self._context.copy()}

    @api.model
    def _rule_eval(self, rule, obj_name, rec):
        expr = rule.code
        space = self._exception_rule_eval_context(obj_name, rec)
        try:
            safe_eval(expr,
                      space,
                      mode='exec',
                      nocopy=True)  # nocopy allows to return 'result'
        except Exception, e:
            raise except_orm(
                _('Error'),
                _('Error when evaluating the invoice exception '
                  'rule:\n %s \n(%s)') % (rule.name, e))
        return space.get('failed', False)

    @api.multi
    def _detect_exceptions(self, invoice_exceptions,
                           line_exceptions):
        self.ensure_one()
        exception_ids = []
        for rule in invoice_exceptions:
            if self._rule_eval(rule, 'invoice', self):
                exception_ids.append(rule.id)

        for invoice_line in self.invoice_line:
            for rule in line_exceptions:
                if rule.id in exception_ids:
                    # we do not matter if the exception as already been
                    # found for an invoice line of this invoice
                    continue
                if self._rule_eval(rule, 'line', invoice_line):
                    exception_ids.append(rule.id)
        return exception_ids
