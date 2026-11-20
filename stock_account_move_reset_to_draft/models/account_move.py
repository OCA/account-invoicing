# Copyright 2024 Tecnativa - Víctor Martínez
# Copyright 2026 ACSONE SA/NV (https://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.fields import Command
from odoo.tools.safe_eval import safe_eval


class AccountMove(models.Model):
    _inherit = "account.move"

    dont_regenerate_valuation = fields.Boolean(
        help="This is a technical field that will be set when resetting the account "
        "move to draft in order to not regenerate stock valuations at revalidation."
    )

    def _get_reset_to_draft_wizard(
        self, move_line_consumed_soft_ids=False, move_line_intertwined_soft_ids=False
    ):
        """
        Returns the wizard to reset account move to draft by showing the lines
        that have been consumed or intertwined.
        """
        if not move_line_consumed_soft_ids:
            move_line_consumed_soft_ids = self.line_ids.browse()
        if not move_line_intertwined_soft_ids:
            move_line_intertwined_soft_ids = self.line_ids.browse()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_account_move_reset_to_draft.stock_account_move_reset_to_draft_act_window"
        )
        context = action.get("context", "{}")
        context = safe_eval(context)
        context.update(
            {
                "default_consumed_move_line_ids": [
                    Command.set(move_line_consumed_soft_ids.ids)
                ],
                "default_intertwined_move_line_ids": [
                    Command.set(move_line_intertwined_soft_ids.ids)
                ],
            }
        )
        action["context"] = context
        return action

    def _force_reset_to_draft(self):
        """
        This will force the reset to draft (called by the wizard).

        Check if user has rights to do it.

        Set the flag to not regenerate the valuations at revalidation.
        """
        if not self._has_right_to_reset_to_draft():
            raise AccessError(_("You don't have rights to reset move to draft."))
        if any(move.state != "posted" for move in self):
            raise ValidationError(
                _("You cannot force account move to Draft if it is not Posted")
            )
        self.write({"dont_regenerate_valuation": True})
        return super().button_draft()

    @api.model
    def _has_right_to_reset_to_draft(self) -> bool:
        return self.env.user.has_group(
            "stock_account_move_reset_to_draft.group_stock_move_force_reset_to_draft"
        )

    def button_draft(self):
        """If it is a purchase invoice, we will create a new SVL for each line with
        the sum of the value in opposite sign.
        """
        moves_to_check = self.sudo().filtered(
            lambda x: x.is_inbound
            and any(line.stock_valuation_layer_ids for line in x.line_ids)
        )
        if not moves_to_check:
            return super().button_draft()
        line_model = self.env["account.move.line"].browse()
        soft = self._has_right_to_reset_to_draft()
        move_line_intertwined_ids = move_line_consumed_ids = line_model

        # Look for problems in stack valuation
        # If no problem, do the valuation revert in order to be revalidated after
        # If the user has no rights to force the reset, raise errors.
        # If the user has rights to force the reset, warn through a wizard and let
        # the user decides if he reset or not.
        for item in moves_to_check:
            lines_with_valuation = item.line_ids.filtered("stock_valuation_layer_ids")
            move_line_intertwined_ids = (
                lines_with_valuation._check_intertwined_valuation_at_draft(soft)
            )
            move_line_consumed_ids = (
                lines_with_valuation._check_consumed_valuation_at_draft(soft)
            )
            if not move_line_consumed_ids and not move_line_intertwined_ids:
                lines_with_valuation._revert_stock_valuation_at_draft()
        if soft and (move_line_consumed_ids or move_line_intertwined_ids):
            return self._get_reset_to_draft_wizard(
                move_line_consumed_ids, move_line_intertwined_ids
            )
        return super().button_draft()

    def _post(self, soft=True):
        """
        Validate account move without regenerating stock valuations.
        """
        moves_without_valuation = self.filtered(
            "dont_regenerate_valuation"
        ).with_context(move_reverse_cancel=True)
        if moves_without_valuation:
            moves = super(AccountMove, moves_without_valuation)._post(soft=soft)
            moves_without_valuation.dont_regenerate_valuation = False
            return moves | super(AccountMove, (self - moves_without_valuation))._post(
                soft=soft
            )
        return super()._post(soft=soft)

    def _compute_show_reset_to_draft_button(self):
        """Overwrite the value only if it is already posted and with SVLs.
        We use the same fields for filtering that account uses for the
        show_reset_to_draft_button field.
        """
        _self = self.sudo().filtered(
            lambda x: not x.restrict_mode_hash_table
            and x.state in ("posted", "cancel")
            and any(line.stock_valuation_layer_ids for line in x.line_ids)
        )
        for item in self:
            item.show_reset_to_draft_button = True
        return super(AccountMove, self - _self)._compute_show_reset_to_draft_button()
