# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BankAccountMixin(models.AbstractModel):
    _name = "bank.account.mixin"
    _description = "Bank Account Mixin"

    bank_account_id = fields.Many2one(
        "res.partner.bank", string="Recipient Bank", copy=False
    )
    bank_account_id_domain = fields.Binary(compute="_compute_bank_account_id_domain")

    def _compute_bank_account_id_domain(self):
        # Override in inheriting models if needed. The override is responsible for
        # declaring its own dependencies (api.depends, api.depends_context), as the
        # domain returned here is constant and needs none.
        for record in self:
            record.bank_account_id_domain = []
