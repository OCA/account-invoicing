# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SalesTeam(models.Model):
    _inherit = "crm.team"

    bank_account_id = fields.Many2one(
        "res.partner.bank",
        domain="[('partner_id', 'in', member_company_ids)]",
        help="Select a bank account belonging to the company's partner",
    )
