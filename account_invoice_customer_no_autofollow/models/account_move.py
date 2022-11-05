# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        partner_ids = partner_ids or []
        if (
            self.env.context.get("invoice_no_auto_follow")
            and self.partner_id.id in partner_ids
        ):
            partner_ids.remove(self.partner_id.id)
        return super(AccountMove, self).message_subscribe(
            partner_ids, channel_ids, subtype_ids
        )

    @api.model_create_multi
    def create(self, values):
        return super(
            AccountMove,
            self.with_context(
                invoice_no_auto_follow=self._partner_disable_autofollow()
            ),
        ).create(values)

    def action_post(self):
        return super(
            AccountMove,
            self.with_context(
                invoice_no_auto_follow=self._partner_disable_autofollow()
            ),
        ).action_post()

    def _partner_disable_autofollow(self):
        """Returns the state of the "Customer disable autofollow" option
        Returns:
            bool: Option status
        """
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "invoice_customer_no_autofollow.invoice_partner_no_autofollow", False,
            )
        )
