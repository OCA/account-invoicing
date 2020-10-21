# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import safe_eval


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.model_create_multi
    def create(self, vals_list):
        invoices = super().create(vals_list)
        invoices.apply_transmit_method_substitutions()
        return invoices

    @api.multi
    def get_substitution_transmit_method(self, substitution_rules):
        transmit_method_id = False
        for substitution_rule in substitution_rules:
            domain = safe_eval(substitution_rule.domain) + [
                ("id", "in", self.ids)
            ]
            if self.search(domain):
                if (
                    transmit_method_id
                    and transmit_method_id
                    != substitution_rule.transmit_method_id
                ):
                    # conflict between rules, we set the transmit
                    return False
                transmit_method_id = substitution_rule.transmit_method_id
        return transmit_method_id

    @api.multi
    def apply_transmit_method_substitutions(self):
        substitution_rule_model = self.env["transmit.method.substitution.rule"]
        substitution_rules_by_company = (
            substitution_rule_model.get_substitution_rules_by_company()
        )
        for group in self.read_group(
            [("id", "in", self.ids), ("transmit_method_id", "!=", False)],
            ["id"],
            ["company_id"],
        ):
            invoices = self.search(group["__domain"])
            company_id = (
                group["company_id"][0] if group["company_id"] else False
            )
            transmit_method_id = invoices.get_substitution_transmit_method(
                substitution_rules_by_company.get(company_id, [])
            )
            if transmit_method_id:
                invoices.write({"transmit_method_id": transmit_method_id.id})
