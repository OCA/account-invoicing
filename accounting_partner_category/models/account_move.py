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
        readonly=False,
        store=True,
        compute="_compute_category_ids",
        help="Tags when partner was added to the invoice.",
    )

    @api.depends("partner_id")
    def _compute_category_ids(self):
        for rec in self:
            rec.category_ids = (
                rec.partner_id.commercial_partner_id.accounting_category_ids
            )
