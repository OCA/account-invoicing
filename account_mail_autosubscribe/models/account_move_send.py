# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_default_mail_partner_ids(self, move, mail_template, mail_lang):
        partners = super()._get_default_mail_partner_ids(move, mail_template, mail_lang)
        autosubscribe_followers = (
            mail_template.use_autosubscribe_followers
            and not self.env.context.get("no_autosubscribe_followers")
        )
        if autosubscribe_followers and partners:
            ResModel = self.env[mail_template.model]
            partners |= ResModel._message_get_autosubscribe_followers(partners)
        return partners
