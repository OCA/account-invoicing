# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    require_approver_in_vendor_bills = fields.Boolean(
        string="Require approver in vendor bills"
    )
    validation_approver_tier_definition_id = fields.Many2one(
        comodel_name="tier.definition", string="Bill approval tier definition"
    )
