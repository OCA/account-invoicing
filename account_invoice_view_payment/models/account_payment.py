# Copyright 2017 ForgeFlow S.L.
#        (https://www.forgeflow.com)
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
