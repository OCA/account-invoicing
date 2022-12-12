# Copyright 2022 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"

    category_ids = fields.Many2many(
        "accounting.partner.category",
        string="Tags",
        help="Tags when partner was added to the invoice.",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        super()._onchange_partner_id()
        self.category_ids = (
            self.partner_id.commercial_partner_id.accounting_category_ids
        )
