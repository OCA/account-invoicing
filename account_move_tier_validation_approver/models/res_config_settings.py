# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    require_approver_in_vendor_bills = fields.Boolean(
        string="Require Approver In Vendor Bills",
        help="Requires adding an approver before a vendor bill can be posted.",
        related="company_id.require_approver_in_vendor_bills",
        readonly=False,
    )

    def set_values(self):
        tier_definition = self.company_id.validation_approver_tier_definition_id
        if not tier_definition:
            field = self.env["ir.model.fields"].search(
                [("model", "=", "account.move"), ("name", "=", "approver_id")]
            )
            tier_definition = self.env["tier.definition"].create(
                {
                    "model_id": self.env["ir.model"]
                    .search([("model", "=", "account.move")])
                    .id,
                    "review_type": "field",
                    "name": "Validation with Approver field",
                    "reviewer_field_id": field.id,
                    "definition_domain": "[('type', '=', 'in_invoice')]",
                    "approve_sequence": True,
                    "active": self.require_approver_in_vendor_bills,
                }
            )
            self.company_id.validation_approver_tier_definition_id = tier_definition
        if self.require_approver_in_vendor_bills:
            tier_definition.action_unarchive()
        else:
            tier_definition.action_archive()
        return super().set_values()
