# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TransmitMethodSubstitutionRule(models.Model):

    _name = "transmit.method.substitution.rule"
    _description = "Transmit Method Substitution Rule"

    name = fields.Char(required=True)
    domain = fields.Char(string="Domain", required=True, default="[]")
    transmit_method_id = fields.Many2one(
        comodel_name="transmit.method", string="Transmit Method", required=True
    )
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
    )

    @api.model
    def get_substitution_rules_by_company(self):
        substitution_rules_by_company = {}
        for group in self.read_group([], ["id"], ["company_id"]):
            if group["company_id"]:
                company_id = group["company_id"][0]
                domain = [
                    "|",
                    ("company_id", "=", company_id),
                    ("company_id", "=", False),
                ]
                substitution_rules_by_company[company_id] = self.search(domain)
        return substitution_rules_by_company
