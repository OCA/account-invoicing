# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "base.cancel.confirm"]

    _has_cancel_reason = "optional"  # ["no", "optional", "required"]

    def button_cancel(self):
        cancel_res_model = self.env.context.get("cancel_res_model", False)
        cancel_res_ids = self.env.context.get("cancel_res_ids", False)
        cancel_method = self.env.context.get("cancel_method", False)
        # cancel from payment
        if cancel_res_model == "account.payment" and cancel_method == "action_cancel":
            docs = self.env[cancel_res_model].browse(cancel_res_ids)
            cancel_reason = ", ".join(
                docs.filtered("cancel_reason").mapped("cancel_reason")
            )
            self.write({"cancel_confirm": True, "cancel_reason": cancel_reason})
        if not self.filtered("cancel_confirm"):
            return self.open_cancel_confirm_wizard()
        return super().button_cancel()

    def button_draft(self):
        self.clear_cancel_confirm_data()
        return super().button_draft()
