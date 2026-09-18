# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    invoice_warn_msg = fields.Text(compute="_compute_invoice_warn_msg")

    @api.depends(
        "move_type",
        "state",
        "partner_id.invoice_warn",
        "partner_id.parent_id.invoice_warn",
    )
    def _compute_invoice_warn_msg(self):
        for rec in self:
            if (
                rec.partner_id
                and rec.move_type in ("out_invoice", "out_refund")
                and rec.state == "draft"
            ):
                if (
                    rec.partner_id.parent_id
                    and rec.partner_id.parent_id.invoice_warn == "warning"
                ):
                    rec.invoice_warn_msg = rec.partner_id.parent_id.invoice_warn_msg
                    if rec.partner_id.invoice_warn == "warning":
                        rec.invoice_warn_msg += "\n%s" % rec.partner_id.invoice_warn_msg
                    continue
                elif rec.partner_id.invoice_warn == "warning":
                    rec.invoice_warn_msg = rec.partner_id.invoice_warn_msg
                    continue
            rec.invoice_warn_msg = False
