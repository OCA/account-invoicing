# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    debit_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Debit Note",
        help="Reference to the origin invoice that create this debit note",
    )
    debit_move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="debit_move_id",
        string="Debit Notes",
        readonly=True,
        help="List all debit notes being created by this invoice",
    )

    def _get_debitnote_vals(self, default_values):
        self.ensure_one()
        move_vals = self.copy_data(default=default_values)[0]
        return move_vals

    def _create_debitnote(self, default_values_list=None):
        if not default_values_list:
            default_values_list = [{} for move in self]

        move_vals_list = []
        for move, default_values in zip(self, default_values_list):
            default_values.update(
                {
                    "type": move.type,
                    "debit_move_id": move.id,
                    "invoice_origin": move.name,
                }
            )
            move_vals_list.append(move._get_debitnote_vals(default_values))

        debit_notes = self.env["account.move"].create(move_vals_list)
        for move, debit_note in zip(
            self, debit_notes.with_context(check_move_validity=False)
        ):
            # Update amount_currency if the date has changed.
            if move.date != debit_note.date:
                for line in debit_note.line_ids:
                    if line.company_currency_id:
                        line._onchange_currency()
            debit_note._recompute_dynamic_lines(recompute_all_taxes=False)
        debit_notes._check_balanced()
        return debit_notes

    def _get_sequence(self):
        journal = self.journal_id
        if self.debit_move_id:
            return journal.debitnote_sequence_id
        return super()._get_sequence()
