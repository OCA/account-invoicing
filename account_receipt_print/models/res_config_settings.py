# Copyright 2024 Sergio Zanchetta - PNLUG APS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_amount_in_words = fields.Boolean(
        string="Show Amount in Words",
        config_parameter="account_receipt_print.show_amount_in_words",
    )
