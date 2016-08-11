# -*- coding: utf-8 -*-
# © 2016 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountInvoiceExceptionConfirm(models.TransientModel):

    _name = 'account.invoice.exception.confirm'

    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    exception_ids = fields.Many2many('sale.exception',
                                     string='Exceptions to resolve',
                                     readonly=True)
    ignore = fields.Boolean('Ignore Exceptions')

    @api.model
    def default_get(self, field_list):
        result = super(AccountInvoiceExceptionConfirm, self).default_get(
            field_list)
        invoice_obj = self.env['account.invoice']
        invoice_id = self.env.context.get('active_ids')
        assert len(invoice_id) == 1, "Only 1 ID accepted, got %r" % invoice_id
        invoice_id = invoice_id[0]
        invoice = invoice_obj.browse(invoice_id)
        exception_ids = [e.id for e in invoice.exception_ids]
        result.update({'exception_ids': [(6, 0, exception_ids)]})
        result.update({'invoice_id': invoice_id})
        return result

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.invoice_id.ignore_exceptions = True
        return {'type': 'ir.actions.act_window_close'}
