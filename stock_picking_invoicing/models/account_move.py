# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_cancel(self):
        """
        Inherit to update related picking as '2binvoiced' when the invoice is
        cancelled (only for invoices, not refunds)
        :return: bool
        """
        result = super().button_cancel()
        pickings = self.filtered(
            lambda i: i.picking_ids and i.move_type in ["out_invoice", "in_invoice"]
        ).mapped("picking_ids")
        self.mapped("invoice_line_ids.move_line_ids")._set_as_2binvoiced()
        pickings._set_as_2binvoiced()
        return result

    def button_draft(self):
        result = super().button_draft()
        pickings = self.filtered(
            lambda i: i.picking_ids and i.move_type in ["out_invoice", "in_invoice"]
        ).mapped("picking_ids")
        self.mapped("invoice_line_ids.move_line_ids")._set_as_invoiced()
        pickings._set_as_invoiced()
        return result

    def unlink(self):
        """
        Inherit the unlink to update related picking as "2binvoiced"
        (only for invoices, not refunds)
        :return:
        """
        pickings = self.filtered(
            lambda i: i.picking_ids and i.move_type in ["out_invoice", "in_invoice"]
        ).mapped("picking_ids")
        self.mapped("invoice_line_ids.move_line_ids")._set_as_2binvoiced()
        pickings._set_as_2binvoiced()
        return super().unlink()

    def _reverse_moves(self, default_values_list=None, cancel=False):
        reverse_moves = super()._reverse_moves(
            default_values_list=default_values_list, cancel=cancel
        )
        for move, reverse_move in zip(self, reverse_moves):
            for line in move.invoice_line_ids:
                reverse_line = reverse_move.invoice_line_ids.filtered(
                    lambda l: l.product_id == line.product_id
                )
                reverse_line.move_line_ids = line.move_line_ids.ids

        return reverse_moves
