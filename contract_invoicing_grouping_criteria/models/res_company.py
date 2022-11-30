from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_contract_invoicing_grouping_criteria_id = fields.Many2one(
        string="Default Contracts Invoicing Grouping Criteria",
        comodel_name="contract.invoicing.grouping.criteria",
    )
