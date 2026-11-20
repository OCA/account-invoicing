# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_show_customer_code = fields.Boolean(
        compute="_compute_partner_show_customer_code"
    )

    @api.depends("move_type")
    def _compute_partner_show_customer_code(self):
        for move in self:
            move.partner_show_customer_code = move.is_sale_document()
