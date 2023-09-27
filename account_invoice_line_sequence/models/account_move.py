# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Forgeflow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sequence2 = fields.Integer(
        help="Shows the sequence of this line in the invoice.",
        string="Sequence",
        store=True,
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    def _reset_sequence(self):
        # This part is just modifying sequences and so does not need a check
        for rec in self.with_context(check_move_validity=False):
            for current_seq, line in enumerate(
                rec.invoice_line_ids.filtered(lambda x: not x.display_type).sorted(
                    "sequence"
                ),
                start=1,
            ):
                line.sequence2 = current_seq

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
