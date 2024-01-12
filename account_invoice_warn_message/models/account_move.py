# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .res_company import INVOICE_WARN_MESSAGE_SELECTION

INVOICE_WARN_MESSAGE_SEL_MAPPING = {
    INVOICE_WARN_MESSAGE_SELECTION[0][0]: ["out_invoice", "out_refund"],
    INVOICE_WARN_MESSAGE_SELECTION[1][0]: ["in_invoice", "in_refund"],
    INVOICE_WARN_MESSAGE_SELECTION[2][0]: [
        "out_invoice",
        "out_refund",
        "in_invoice",
        "in_refund",
    ],
}


class AccountMove(models.Model):

    _inherit = "account.move"

    invoice_warn_msg = fields.Text(compute="_compute_invoice_warn_msg")

    @api.depends(
        "type", "state", "partner_id.invoice_warn", "partner_id.parent_id.invoice_warn"
    )
    def _compute_invoice_warn_msg(self):
        move_types_warn = INVOICE_WARN_MESSAGE_SEL_MAPPING[
            self.env.company.invoice_warn_message_type
        ]
        for rec in self:
            if rec.partner_id and rec.type in move_types_warn and rec.state == "draft":
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
