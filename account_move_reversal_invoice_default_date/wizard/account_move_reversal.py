from odoo import api, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    @api.model
    def default_get(self, fields):
        res = super(AccountMoveReversal, self).default_get(fields)
        move_ids = (
            self.env["account.move"].browse(self.env.context["active_ids"])
            if self.env.context.get("active_model") == "account.move"
            else self.env["account.move"]
        )
        res["date"] = max(move_ids.mapped("date"))
        return res
