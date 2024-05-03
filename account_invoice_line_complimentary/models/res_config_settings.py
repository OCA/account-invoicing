#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings (models.TransientModel):
    _inherit = 'res.config.settings'

    complimentary_account_id = fields.Many2one(
        related='company_id.complimentary_account_id',
        readonly=False,
    )
