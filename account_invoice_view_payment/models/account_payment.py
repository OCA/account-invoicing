# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#        (https://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def post_and_open_payment(self):
        self.action_post()
        res = {
            "name": _("Payments"),
            "views": [(False, "form")],
            "res_id": self.id,
            "res_model": "account.payment",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }
        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def create_payment_and_open(self):
        account_move_model = self.env["account.move"]
        payment_model = self.env["account.payment"]
        payments = payment_model
        for _payment_vals in account_move_model.search(
            [("id", "in", self.env.context.get("active_ids", False))]
        ):
            vals = self._create_payment_vals_from_wizard()
            payments += payment_model.create(vals)
        payments.action_post()
        res = {
            "domain": [("id", "in", payments.ids), ("state", "=", "posted")],
            "name": _("Payments"),
            "view_mode": "tree,form",
            "res_model": "account.payment",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }
        return res
