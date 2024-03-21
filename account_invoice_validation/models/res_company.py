# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    validation_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Default invoice approver user",
        help="Default approver user for purchase invoice/refunds",
    )
