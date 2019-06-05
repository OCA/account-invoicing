# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """Create invoice note lines with notes from the sale order"""
        invoice_ids = super().action_invoice_create(
            grouped=grouped, final=final
        )
        if self.env.context.get('_copy_notes'):
            note_lines_vals = []
            for sale_order in self:
                invoice = sale_order.invoice_ids.filtered(
                    lambda i: i.id in invoice_ids
                )
                if not invoice:
                    # The sale order did not generate an invoice
                    continue
                notes_to_create = sale_order.order_line.filtered(
                    lambda l: l.display_type == 'line_note'
                )
                for note in notes_to_create:
                    note_vals = {
                        'origin': sale_order.name,
                        'invoice_id': invoice.id,
                        'sequence': note.sequence,
                        'display_type': 'line_note',
                        'name': note.name
                    }
                    note_lines_vals.append(note_vals)
            self.env['account.invoice.line'].create(note_lines_vals)
        return invoice_ids
