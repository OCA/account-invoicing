# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2022 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    refund_invoice_ids = fields.One2many(
        "account.move", "reversed_entry_id", string="Refund Invoices", readonly=True
    )

    def _reverse_moves(self, default_values_list=None, cancel=False):
        reverse_moves = super()._reverse_moves(
            default_values_list=default_values_list, cancel=cancel
        )
        if self.env.context.get("link_origin_line", False):
            for move in reverse_moves:
                if move.move_type in ("out_refund", "in_refund"):
                    refund_lines = move.line_ids.filtered(
                        lambda x: x.display_type == "product"
                    )
                    for i, line in enumerate(
                        self.invoice_line_ids.filtered(
                            lambda x: x.display_type == "product"
                        )
                    ):
                        if i < len(refund_lines):
                            refund_lines[i].origin_line_id = line.id
        return reverse_moves
