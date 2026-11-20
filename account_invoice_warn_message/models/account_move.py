# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import OrderedSet


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_warn_msg = fields.Text(compute="_compute_invoice_warn_msg")

    @api.depends(
        "move_type",
        "state",
        "partner_id.invoice_warn_msg",
        "partner_id.parent_id.invoice_warn_msg",
    )
    def _compute_invoice_warn_msg(self):
        for move in self:
            if (
                move.partner_id
                and move.move_type in ("out_invoice", "out_refund")
                and move.state == "draft"
            ):
                warnings = OrderedSet()
                if parent := move.partner_id.parent_id:
                    if msg := parent.invoice_warn_msg:
                        warnings.add((parent.name or parent.display_name) + " - " + msg)
                if msg := move.partner_id.invoice_warn_msg:
                    partner = move.partner_id
                    warnings.add((partner.name or partner.display_name) + " - " + msg)
                move.invoice_warn_msg = "\n".join(warnings) if warnings else False
            else:
                move.invoice_warn_msg = False
