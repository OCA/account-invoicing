# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>                                               
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html). 
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_cancel_draft(self):
        """Also reset state in SO, if SO in Invoice Exception."""
        sale_model = self.env['sale.order']
        super(AccountInvoice, self).action_cancel_draft()
        for this in self:
            so = sale_model.search([('invoice_ids', '=', this.id)])
            so.signal_workflow('invoice_corrected')
        return True
