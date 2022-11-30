from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    res_default_contract_invoicing_grouping_criteria_id = fields.Many2one(
        related="company_id.default_contract_invoicing_grouping_criteria_id",
        readonly=False,
    )
