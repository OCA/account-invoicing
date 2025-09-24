# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    show_discount_warning_label = fields.Boolean(
        compute="_compute_show_discount_warning_label"
    )

    @api.depends(
        "invoice_line_ids.discount_fixed",
        "invoice_line_ids.discount1",
        "invoice_line_ids.discount2",
        "invoice_line_ids.discount3",
    )
    def _compute_show_discount_warning_label(self):
        for move in self:
            move.show_discount_warning_label = any(
                line.discount_fixed
                and (line.discount1 or line.discount2 or line.discount3)
                for line in move.invoice_line_ids
            )
