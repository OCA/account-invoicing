# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    move_name = fields.Char(
        string="Force Number",
        readonly=False,
        default=False,
        copy=False,
        help="""Force invoice number. Use this field if
        you don't want to use the default numbering.""",
    )

    def unlink(self):
        for move in self:
            if move.move_name:
                raise UserError(
                    _(
                        """You cannot delete an invoice after it has been validated"""
                        '''(and received a number). You can set it back to "Draft"'''
                        """state and modify its content, then re-confirm it."""
                    )
                )
        return super(AccountMove, self).unlink()

    def action_post(self):
        for move in self:
            if move.move_name:
                move.write({"name": move.move_name})
        return super(AccountMove, self).action_post()
