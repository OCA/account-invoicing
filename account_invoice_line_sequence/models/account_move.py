# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Forgeflow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sequence2 = fields.Integer(
        help="Shows the sequence of this line in the invoice.",
        string="Line Number",
        store=True,
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_invoice_sequence_lines(self):
        """Return invoice lines that must receive a sequence number."""
        self.ensure_one()
        return self.invoice_line_ids.filtered(
            lambda line: line.display_type not in ("line_section", "line_note")
        ).sorted("sequence")

    def _reset_sequence(self):
        """Reset invoice line sequence numbers.

        Sections and notes must not be numbered. Product/accountable lines are
        numbered from 1 according to their invoice line order.
        """
        for move in self.with_context(check_move_validity=False):
            sequence_lines = move._get_invoice_sequence_lines()
            non_sequence_lines = move.invoice_line_ids - sequence_lines

            for line in non_sequence_lines:
                line.sequence2 = 0

            for current_sequence, line in enumerate(sequence_lines, start=1):
                line.sequence2 = current_sequence

    @api.onchange("invoice_line_ids")
    def _onchange_invoice_line_ids_line_sequence(self):
        self._reset_sequence()

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result._reset_sequence()
        return result

    def write(self, values):
        reset_sequence = "invoice_line_ids" in values
        res = super().write(values)
        if reset_sequence:
            self._reset_sequence()
        return res
