# Copyright 2022 Darío Cruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    account_move_tag_ids = fields.Many2many(
        "account.move.tag", string="Account Move Tags",
    )
