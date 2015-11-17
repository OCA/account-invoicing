# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_invoice_create(
            self, grouped=False, states=None, date_invoice=False):
        """
            Pass the incoterm to the invoice from the sales order
        """
        invoice_id = super(SaleOrder, self).action_invoice_create(
            grouped=grouped, states=states, date_invoice=date_invoice)
        self.env['account.invoice'].browse(invoice_id).write(
            {'incoterm': self.incoterm.id})
        return invoice_id
