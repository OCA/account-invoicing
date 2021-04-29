# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountExceptionConfirm(models.TransientModel):
    _inherit = "account.exception.confirm"

    def action_confirm(self):
        self.ensure_one()
        if self.ignore and self.related_model_id.post_block_id:
            self.related_model_id.button_release_post_block()
        return super().action_confirm()
