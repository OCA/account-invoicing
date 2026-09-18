# Copyright 2017 ForgeFlow S.L.
#        (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_view_payments(self):
        """
        This function returns an action that display existing payments of given
        account moves.
        When only one found, show the payment immediately.
        """
        if self.move_type in ("in_invoice", "in_refund"):
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "account.action_account_payments_payable"
            )
        else:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "account.action_account_payments"
            )
        reconciles = self._get_reconciled_info_JSON_values()
        payment = []
        for rec in reconciles:
            payment.append(rec["account_payment_id"])

        # choose the view_mode accordingly
        if len(reconciles) != 1:
            action["domain"] = "[('id', 'in', " + str(payment) + ")]"
        else:
            res = self.env.ref("account.view_account_payment_form", False)
            action["views"] = [(res and res.id or False, "form")]
            action["res_id"] = payment and payment[0] or False
        return action
