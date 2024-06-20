# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def js_remove_outstanding_partial(self, partial_id):
        """Auto cancel payment related account move"""
        res = super().js_remove_outstanding_partial(partial_id)
        self.ensure_one()
        self.payment_id.action_draft()
        self.payment_id.action_cancel()
        return res
