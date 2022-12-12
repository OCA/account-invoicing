# Copyright 2022 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from random import randint

from odoo import fields, models


class AccountingPartnerCategory(models.Model):
    _description = "Partner accounting Tags"
    _name = "accounting.partner.category"
    _order = "name"

    _sql_constraints = [
        (
            "name_uniq",
            "UNIQUE(name)",
            "The name must be unique!",
        ),
    ]

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Tag Name", required=True, translate=True)
    color = fields.Integer(string="Color Index", default=_get_default_color)
    active = fields.Boolean(
        default=True,
        help="The active field allows you to hide the category without removing it.",
    )
