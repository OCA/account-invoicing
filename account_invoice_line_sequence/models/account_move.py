# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Forgeflow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import config


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sequence = fields.Integer(
        help="Shows the sequence of this line in the invoice.",
        default=9999,
        string="original sequence",
    )

    # shows sequence on the invoice line
    sequence2 = fields.Integer(
        help="Shows the sequence of this line in the invoice.",
        related="sequence",
        string="Sequence",
        store=True,
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("invoice_line_ids")
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in invoice lines.
        Then we add 1 to this value for the next sequence.
        This value is given to the context of the o2m field in the view.
        So when we create new invoice lines, the sequence is automatically
        added as :  max_sequence + 1
        """
        for invoice in self:
            invoice.max_line_sequence = (
                max(invoice.mapped("invoice_line_ids.sequence") or [0]) + 1
            )

    max_line_sequence = fields.Integer(
        string="Max sequence in lines", compute="_compute_max_line_sequence", store=True
    )

    def _reset_sequence(self):
        # This part is just modifying sequences and so does not need a check
        for rec in self.with_context(check_move_validity=False):
            for current_seq, line in enumerate(
                rec.invoice_line_ids.sorted("sequence"), start=1
            ):
                line.sequence = current_seq

    def write(self, values):
        res = super(AccountMove, self).write(values)
        if not config["test_enable"] or self.env.context.get(
            "test_account_invoice_line_sequence"
        ):
            self._reset_sequence()
        return res
