# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SalesTeam(models.Model):
    _name = "crm.team"
    _inherit = ["crm.team", "bank.account.mixin"]

    @api.depends("member_company_ids")
    def _compute_bank_account_id_domain(self):
        for team in self:
            team.bank_account_id_domain = [
                ("partner_id", "in", team.member_company_ids.mapped("partner_id").ids)
            ]
