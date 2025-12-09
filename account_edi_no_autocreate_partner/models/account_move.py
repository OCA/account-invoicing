# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):

    _inherit = "account.move"

    def action_post(self):
        partner_not_found = self.env.ref(
            "account_edi_no_autocreate_partner.partner_not_found"
        )
        for move in self:
            if move.partner_id == partner_not_found:
                raise UserError(
                    _(
                        "You must assign a proper vendor before posting this invoice. "
                        "The fallback 'Partner Not Found' partner cannot be used on "
                        "posted moves."
                    )
                )
        return super().action_post()
