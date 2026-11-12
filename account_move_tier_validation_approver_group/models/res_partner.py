# Copyright 2025 360 ERP
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    approver_group_id = fields.Many2one(
        "res.groups", string="Approver of Vendor Bills group"
    )
