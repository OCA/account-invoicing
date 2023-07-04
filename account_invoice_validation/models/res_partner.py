# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    validation_user_id = fields.Many2one(
        "res.users",
        "Validation user",
        help="User in charge of the invoices/refunds validation.",
    )

    validation_user_id_domain = fields.Binary(
        string="validation user domain",
        help="Dynamic domain for validation user",
        compute="_compute_validation_user_id_domain",
    )

    use_invoice_first_approval = fields.Binary(
        help="Use a first level of approbation: approver can be set on vendors",
        compute="_compute_use_invoice_first_approval",
    )

    def _compute_use_invoice_first_approval(self):
        self.use_invoice_first_approval = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account_invoice_validation.use_invoice_first_approval")
        )

    def _compute_validation_user_id_domain(self):
        """
        User should have group_account_invoice_validation
        User should have access to company of partner (if defined)
        """
        for rec in self:
            domain = [
                (
                    "id",
                    "in",
                    self.env.ref(
                        "account_invoice_validation.group_account_invoice_validation"
                    ).users.ids,
                )
            ]

            if self.company_id:
                domain.append(
                    (
                        "company_ids",
                        "in",
                        [self.company_id.id],
                    )
                )

            rec.validation_user_id_domain = domain
