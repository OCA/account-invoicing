# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_invoice_line_key_cols(self):
        res = super()._get_invoice_line_key_cols()
        res.append("purchase_line_id")
        return res
