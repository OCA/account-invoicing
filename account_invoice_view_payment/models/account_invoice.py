# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#        (https://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_view_payments(self):
        """
        This function returns an action that display existing payments of given
        account invoices.
        When only one found, show the payment immediately.
        """
        if self.type in ("in_invoice", "in_refund"):
            action = self.env.ref("account.action_account_payments_payable")
        else:
            action = self.env.ref("account.action_account_payments")

        result = action.read()[0]

        # choose the view_mode accordingly
        if len(self.payment_ids) != 1:
            result["domain"] = "[('id', 'in', " + str(self.payment_ids.ids) + ")]"
        elif len(self.payment_ids) == 1:
            res = self.env.ref("account.view_account_payment_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.payment_ids.id
        return result
