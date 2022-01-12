# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _prepare_reinvoice_reversal(self):
        return {
            "ref": _("Reversal of: %s") % (self.name),
            "journal_id": self.journal_id.id,
            "invoice_payment_term_id": None,
            "invoice_user_id": self.invoice_user_id.id,
        }

    def _reverse_move_vals(self, default_values, cancel=True):
        if self.env.context.get("reinvoice_refund"):
            if self.move_type == "out_refund":
                default_values["move_type"] = "out_invoice"
            elif self.move_type == "in_refund":
                default_values["move_type"] = "in_invoice"
        return super(AccountMove, self)._reverse_move_vals(
            default_values, cancel=cancel
        )

    def action_refund_reinvoice(self):
        self.ensure_one()
        reverse_move = self.with_context(reinvoice_refund=True)._reverse_moves(
            [self._prepare_reinvoice_reversal()], False
        )
        return reverse_move.get_formview_action()
