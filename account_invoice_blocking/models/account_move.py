# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    blocked = fields.Boolean(
        "No Follow-up",
        states={"draft": [("readonly", True)]},
        compute="_compute_move_blocked",
        inverse="_inverse_move_blocked",
    )

    def _get_move_line(self):
        """
        This method searches for payable or receivable move line
        of the invoice
        :returns payable or receivable move line of the invoice
        """
        self.ensure_one()
        type_receivable = self.env.ref("account.data_account_type_receivable")
        type_payable = self.env.ref("account.data_account_type_payable")
        user_type = type_receivable | type_payable
        return self.line_ids.filtered(lambda r: r.account_id.user_type_id in user_type)

    def _update_blocked(self, value):
        """
        This method updates the boolean field 'blocked' of the move line
        of the passed invoice with the passed value
        :param value: value to set to the 'blocked' field of the move line
        """
        self.ensure_one()
        move_line_ids = self._get_move_line()
        move_line_ids.write({"blocked": value})

    def _inverse_move_blocked(self):
        """
        Inverse method of the computed field 'blocked'
        This method calls the update of the invoice's move line based on
        the value of the field 'blocked'
        """
        for invoice in self:
            invoice._update_blocked(invoice.blocked)

    @api.depends("line_ids", "line_ids.blocked")
    def _compute_move_blocked(self):
        """
        This method set the value of the field 'blocked' to True
        If every line of the move is actually blocked
        """
        for move in self:
            move_lines = move._get_move_line()
            move.blocked = (
                all(line.blocked for line in move_lines) if move_lines else False
            )
