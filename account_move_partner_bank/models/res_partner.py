# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "bank.account.mixin"]

    bank_account_id = fields.Many2one(company_dependent=True)

    @api.depends_context("company")
    @api.depends("company_id")
    def _compute_bank_account_id_domain(self):
        for partner in self:
            if partner.company_id:
                partner.bank_account_id_domain = [
                    ("partner_id", "=", partner.company_id.partner_id.id)
                ]
            else:
                partner.bank_account_id_domain = [
                    ("partner_id", "=", self.env.company.partner_id.id)
                ]
