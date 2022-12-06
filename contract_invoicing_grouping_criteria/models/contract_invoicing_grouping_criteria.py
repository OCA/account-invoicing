from odoo import fields, models


class ContractInvoicingGroupingCriteria(models.Model):
    _name = "contract.invoicing.grouping.criteria"
    _description = "Contracts Invoicing Grouping Criteria"

    name = fields.Char()
    field_ids = fields.Many2many(
        string="Contract Grouping Fields",
        comodel_name="ir.model.fields",
        relation="contract_invoicing_grouping_criteria_field_rel",
        domain="[('model', '=', 'contract.contract')]",
        help="Fields used for grouping contracts when invoicing. "
        "Invoicing address, company and currency will always be applied.",
    )
    line_field_ids = fields.Many2many(
        string="Contract Line Grouping Fields",
        comodel_name="ir.model.fields",
        relation="contract_line_invoicing_grouping_criteria_field_rel",
        domain="[('model', '=', 'contract.line')]",
        help="Fields used for grouping contracts when invoicing. ",
    )
