#  Copyright 2021 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner (models.Model):
    _inherit = 'res.partner'

    discounting_type = fields.Selection(
        string="Discounting type",
        selection=[
            ('additive', 'Additive'),
            ('multiplicative', 'Multiplicative'),
        ],
        default="multiplicative",
        required=True,
        help="""
        Specifies whether discounts should be additive or multiplicative.
        Additive discounts are summed first and then applied.
        Multiplicative discounts (default) are applied sequentially.
        This type of discount will be the default for this partner's invoices.
        """,
    )
