from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    contract_invoicing_grouping_criteria_id = fields.Many2one(
        string="Contracts Invoicing Grouping Criteria",
        comodel_name="contract.invoicing.grouping.criteria",
        help="If empty, company default (if any) or default will be applied.",
    )

    @api.model
    def _commercial_fields(self):
        """Add this field to commercial fields, as it should be propagated
        to children.
        """
        return super()._commercial_fields() + [
            "contract_invoicing_grouping_criteria_id",
        ]
