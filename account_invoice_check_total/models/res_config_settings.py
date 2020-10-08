# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..models.account_move import GROUP_AICT


class AccountConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    group_supplier_inv_check_total = fields.Boolean(
        string="Check Total on Vendor Bills", implied_group=GROUP_AICT
    )
