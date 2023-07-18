# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    validation_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Main Invoice Approver User",
        related="company_id.validation_user_id",
        help="Default approver user for purchase invoice/refunds",
        readonly=False,
    )

    use_invoice_first_approval = fields.Boolean(
        help="Use a first level of approbation: approver can be set on vendors",
        config_parameter="account_invoice_validation.use_invoice_first_approval",
    )
