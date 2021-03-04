# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["open", "paid"]

    @api.model
    def _get_under_validation_exceptions(self):
        res = super()._get_under_validation_exceptions()
        if self.env.context.get("invoice_tier_validation_allow_write"):
            res += ["move_id", "date", "move_name", "date_due", "date_invoice"]
        return res

    @api.multi
    def _check_allow_write_under_validation(self, vals):
        allow_write = all([invoice.state == "draft" for invoice in self])
        ctx = self.env.context.copy()
        ctx["invoice_tier_validation_allow_write"] = allow_write
        res = super(AccountInvoice, self.with_context(ctx))\
            ._check_allow_write_under_validation(vals)
        return res
