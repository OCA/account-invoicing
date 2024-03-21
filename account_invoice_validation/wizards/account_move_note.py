# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, fields, models


class AccountMoveNote(models.TransientModel):
    _name = "account.move.note"
    _description = "Adds a note to an account move"

    note = fields.Char(required=True)
    account_move_id = fields.Many2one(
        "account.move",
        "Account move",
        default=lambda self: self.env.context.get("active_id", False),
    )
    date = fields.Date()

    def action_send_note(self):
        """
        Action to send the note to the corresponding account_move
        :return: dict/action
        """
        if self.env.context.get("movingToState") == "refuse":
            self.account_move_id.action_refuse_state_continue(self.note)
        elif self.env.context.get("movingToState") == "assign":
            self.account_move_id.action_assign_continue(self.note)
        elif self.env.context.get("movingToState") == "blocked":
            if not self.date:
                message = _("Please specify a date!")
                raise exceptions.UserError(message)

            self.account_move_id.action_block_state_continue(self.note, self.date)
