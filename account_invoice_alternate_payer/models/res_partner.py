# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    alternate_payer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Alternate Payer",
        help="If set, this will be the partner that we expect to pay or to "
        "be paid by. If not set, the payer is by default the "
        "commercial",
    )
