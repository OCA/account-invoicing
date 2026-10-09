# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_view_product_invoice_lines(self):
        """Return the action opening the mass editable invoice lines list."""
        self.ensure_one()
        return {
            "name": _("Invoice Lines"),
            "type": "ir.actions.act_window",
            "res_model": "account.move.line",
            "view_mode": "list",
            "domain": [
                ("move_id", "=", self.id),
                ("display_type", "in", ("product", "line_section", "line_note")),
            ],
            "views": [
                (
                    self.env.ref(
                        "account_invoice_line_mass_edit.view_invoice_line_list_mass_edit"
                    ).id,
                    "list",
                ),
            ],
            "target": "current",
        }
