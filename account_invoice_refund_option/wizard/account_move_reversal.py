from odoo import Command, api, fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    filter_refund = fields.Boolean(
        string="Select product(s)",
    )
    refund_line_ids = fields.One2many(
        "account.move.reversal.refund.line",
        "wizard_id",
    )

    @api.onchange("filter_refund")
    def onchange_select_product(self):
        if not self.filter_refund:
            self.refund_line_ids = []

    def _prepare_default_reversal(self, move):
        vals = super()._prepare_default_reversal(move)
        if not self.filter_refund or not self.refund_line_ids:
            return vals

        command_move_lines = []
        for refund_line in self.refund_line_ids:
            move_line = self.env["account.move.line"].search(
                [
                    ("move_id", "=", move.id),
                    ("product_id", "=", refund_line.product_id.id),
                ],
                limit=1,
            )
            line_vals = move_line.copy_data({"quantity": refund_line.quantity})
            command_move_lines.append((Command.CREATE, 0, line_vals[0]))
        vals.update(
            {
                "line_ids": command_move_lines,
            }
        )
        return vals
