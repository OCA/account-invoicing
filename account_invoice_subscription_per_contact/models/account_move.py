# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        """Intercept this method so that any change (create/write) auto-defines
        the extra subscribers.
        """
        res = super()._message_auto_subscribe_followers(
            updated_values=updated_values, default_subtype_ids=default_subtype_ids
        )
        if "partner_id" in list(updated_values.keys()):
            invoice_create_subtype = self.env.ref(
                "account_invoice_subscription_per_contact.mt_invoice_new"
            )
            for item in self:
                partners = item.partner_id | item.partner_id.commercial_partner_id
                partner_ids = partners.message_follower_ids.filtered(
                    lambda x: invoice_create_subtype in x.subtype_ids
                ).partner_id
                for partner in partner_ids:
                    res += [(partner.id, default_subtype_ids, False)]
        return res
