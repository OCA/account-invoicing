# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    charge_restocking_fee = fields.Boolean(
        tracking=True,
        help="Tick this box if you wish to charge your customer a fee in "
        "case of return of goods",
        default=False,
    )
