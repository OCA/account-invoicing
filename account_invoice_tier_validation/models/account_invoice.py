# Copyright 2020 ForgeFlow S.L.
# Copyright 2021 Onestein (<https://www.onestein.eu>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import threading

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
            res += [
                "move_id",
                "date",
                "move_name",
                "date_due",
                "date_invoice",
                "reference"
            ]
        return res

    @api.model
    def _skip_tier_validation(self):
        testing = getattr(threading.current_thread(), 'testing', False)
        force_check = self.env.context.get("force_check_tier_validation")
        return testing and not force_check

    @api.multi
    def _check_allow_write_under_validation(self, vals):
        # disable tier validation when running tests
        # to avoid that tests in other modules would be blocked
        if self._skip_tier_validation():
            return True

        # check whether invoice is is draft and pass this info
        # in context to _check_allow_write_under_validation()
        allow_write = all([invoice.state == "draft" for invoice in self])
        ctx = self.env.context.copy()
        ctx["invoice_tier_validation_allow_write"] = allow_write
        res = super(AccountInvoice, self.with_context(ctx))\
            ._check_allow_write_under_validation(vals)
        return res

    def _check_state_conditions(self, vals):
        # disable check state when running tests
        # to avoid that tests in other modules would be blocked
        if self._skip_tier_validation():
            return False
        return super()._check_state_conditions(vals)
