from odoo import fields, models


class ContractInvoicingGroupingCriteria(models.Model):
    _name = "contract.invoicing.grouping.criteria"
    _description = "Contracts Invoicing Grouping Criteria"

    name = fields.Char()
    field_ids = fields.Many2many(
        string="Grouping Fields",
        comodel_name="ir.model.fields",
        domain="[('model', '=', 'contract.contract')]",
        help="Fields used for grouping contracts when invoicing. "
        "Invoicing address, company and currency will always be applied.",
    )
