# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models

from odoo.addons.account.models.account_move import TYPE_REVERSE_MAP

TYPE_REVERSE_MAP.update({"out_refund": "out_invoice", "in_refund": "in_invoice"})


class AccountMove(models.Model):

    _inherit = "account.move"

    def _prepare_reinvoice_reversal(self):
        return {
            "ref": _("Reversal of: %s") % (self.name),
            "journal_id": self.journal_id.id,
            "invoice_payment_term_id": None,
            "invoice_user_id": self.invoice_user_id.id,
        }

    def action_refund_reinvoice(self):
        self.ensure_one()
        reverse_move = self.with_context(reinvoice_refund=True)._reverse_moves(
            [self._prepare_reinvoice_reversal()], False
        )
        return reverse_move.get_formview_action()
