# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    res_default_purchase_invoicing_grouping_criteria_id = fields.Many2one(
        related="company_id.default_purchase_invoicing_grouping_criteria_id",
        readonly=False,
    )
