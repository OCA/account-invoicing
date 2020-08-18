# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["open", "paid"]
