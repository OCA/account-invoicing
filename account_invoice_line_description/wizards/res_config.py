# Copyright 2015 Agile Business Group sagl (https://www.agilebg.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_use_product_description_per_inv_line = fields.Boolean(
        string="Allow using only the product description on the invoice lines",
        implied_group="account_invoice_line_description."
        "group_use_product_description_per_inv_line",
        help="""Allows you to use only product description on the invoice lines.""",
    )
