#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_reverse_receipt(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_view_account_move_reversal"
        )

        if self.is_receipt():
            action["name"] = _("Refund Receipt")
        return action

    def _reverse_move_vals(self, default_values, cancel=True):
        reverse_move_values = super()._reverse_move_vals(default_values, cancel=cancel)
        if self.is_receipt():
            # We have to do this after `super` because `is_refund` variable
            # in `super` method does not manage Receipts.
            # Let the core compute the reverse values as usual,
            # so that it performs everything thinking that this is an Entry.
            # For example, in the taxes the refund repartition lines are used
            # instead of the invoice repartition lines.
            reverse_move_values["move_type"] = self.move_type

            # Inverse quantity instead of amounts
            # because there is no move type dedicated to Receipt Refunds.
            reverse_move_line_commands = reverse_move_values.get("line_ids", [])
            for reverse_move_line_command in reverse_move_line_commands:
                reverse_move_line_values = reverse_move_line_command[2]  # (0, 0, {...})
                reverse_move_line_values.update(
                    {
                        "quantity": -reverse_move_line_values["quantity"],
                    }
                )
        return reverse_move_values
