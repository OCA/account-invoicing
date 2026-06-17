# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        return super(
            AccountMove, self.with_context(mail_auto_subscribe_no_notify=True)
        ).create(vals_list)

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        recipient_data = super()._notify_get_recipients(message, msg_vals, **kwargs)
        mt_comment = self.env.ref("mail.mt_comment")
        if recipient_data and message.subtype_id == mt_comment:
            return [r for r in recipient_data if r.get("type") != "user"]
        return recipient_data
