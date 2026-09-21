# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    accounting_date_comparison = fields.Boolean(
        config_parameter="account_invoice_check_picking_date.accounting_date_comparison"
    )
