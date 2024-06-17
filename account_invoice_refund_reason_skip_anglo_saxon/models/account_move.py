# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        return super(
            AccountMove,
            self - self.filtered(lambda x: x.reason_id.skip_anglo_saxon_entries),
        )._stock_account_prepare_anglo_saxon_out_lines_vals()
