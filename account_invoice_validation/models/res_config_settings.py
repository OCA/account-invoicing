# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    validation_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Default invoice validation user",
        related="company_id.validation_user_id",
        help="Default validation user for purchase invoice/refunds",
        readonly=False,
    )
