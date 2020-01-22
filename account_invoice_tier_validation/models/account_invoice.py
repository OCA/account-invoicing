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
        res = super(AccountInvoice, self)._get_under_validation_exceptions()
        res.append("route_id")
        return res
