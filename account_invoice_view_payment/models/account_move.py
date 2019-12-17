# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#        (https://www.eficent.com)
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
        if self.type in ("in_invoice", "in_refund"):
            action = self.env.ref("account.action_account_payments_payable")
        else:
            action = self.env.ref("account.action_account_payments")
        result = action.read()[0]
        reconciles = self._get_reconciled_info_JSON_values()
        payment = []
        for rec in reconciles:
            payment.append(rec["account_payment_id"])

        # choose the view_mode accordingly
        if len(reconciles) != 1:
            result["domain"] = "[('id', 'in', " + str(payment) + ")]"
        else:
            res = self.env.ref("account.view_account_payment_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = payment[0]
        return result
