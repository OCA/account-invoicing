# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
import logging
from pprint import pformat
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _first_invoice_line_values(self, vals, new_invoice_line):
        super(AccountInvoice, self)._first_invoice_line_values(
            vals, new_invoice_line)
        if new_invoice_line.move_line_ids.ids:
            vals['move_line_ids'] = [
                (6, False, new_invoice_line.move_line_ids.ids)]

    @api.model
    def _merge_invoice_line_values(self, vals, new_invoice_line):
        super(AccountInvoice, self)._merge_invoice_line_values(
            vals, new_invoice_line)
        if 'move_line_ids' in vals:
            vals['move_line_ids'][0][2] += new_invoice_line.move_line_ids.ids
        else:
            vals['move_line_ids'] = [
                (6, False, new_invoice_line.move_line_ids.ids)]

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        """Add picking references to merged invoices."""
        # Store picking invoice states to restore them later
        invoice_states = {
            picking: picking.invoice_state for
            picking in self.mapped('picking_ids')
        }
        invoices_info = super(AccountInvoice, self).do_merge(
            keep_references=keep_references, date_invoice=date_invoice)
        # Restore invoice states
        for picking in invoice_states:
            picking.invoice_state = invoice_states[picking]
        for new_invoice_id in invoices_info:
            new_invoice = self.browse(new_invoice_id)
            origin_invoices = self.browse(invoices_info[new_invoice_id])
            new_invoice.picking_ids = [
                (6, 0, origin_invoices.mapped('picking_ids').ids)]
        return invoices_info
