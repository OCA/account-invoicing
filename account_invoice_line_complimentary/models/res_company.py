#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany (models.Model):
    _inherit = 'res.company'

    complimentary_account_id = fields.Many2one(
        comodel_name='account.account',
    )
