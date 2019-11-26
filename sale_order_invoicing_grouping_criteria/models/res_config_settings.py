# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    res_default_sale_invoicing_grouping_criteria_id = fields.Many2one(
        related='company_id.default_sale_invoicing_grouping_criteria_id',
        readonly=False,
    )
