# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import str2bool


class ResPartner(models.Model):
    _inherit = "res.partner"

    validation_user_id = fields.Many2one(
        "res.users",
        "Approver user",
        help="User in charge of the invoices/refunds approval.",
        company_dependent=True,
    )

    validation_user_id_domain = fields.Binary(
        string="approver user domain",
        help="Dynamic domain for approver user",
        compute="_compute_validation_user_id_domain",
    )

    use_invoice_first_approval = fields.Boolean(
        help="Use a first level of approbation: approver can be set on vendors",
        compute="_compute_use_invoice_first_approval",
    )

    def _compute_use_invoice_first_approval(self):
        self.update(
            {
                "use_invoice_first_approval": str2bool(
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("account_invoice_validation.use_invoice_first_approval")
                )
            }
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
