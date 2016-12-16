# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class WizardUpdateInvoiceSupplierinfo(models.TransientModel):
    _inherit = 'wizard.update.invoice.supplierinfo'

    @api.multi
    def set_supplierinfo_ok(self):
        super(WizardUpdateInvoiceSupplierinfo, self).set_supplierinfo_ok()
        invoice = self.env['account.invoice'].browse(
            self._context['active_id'])
        invoice.signal_workflow('invoice_open')
