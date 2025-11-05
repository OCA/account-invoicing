# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    receipt_status = fields.Selection(
        selection="_get_receipt_status_selection",
        compute="_compute_receipt_status",
        store=True,
        readonly=True,
        index="btree",
    )

    def _get_receipt_status_selection(self):
        return (
            self.env["purchase.order.line"]
            ._fields["line_receipt_status"]
            ._description_selection(self.env)
        )

    @api.depends("invoice_line_ids", "invoice_line_ids.receipt_status")
    def _compute_receipt_status(self):
        for move in self:
            invoice_lines = move.invoice_line_ids.filtered(
                lambda x: x.display_type not in ("line_note", "line_section")
            )
            statuses = set(invoice_lines.mapped("receipt_status"))

            if not statuses or statuses == {False}:
                result = False
            elif statuses == {"full", False} or statuses == {"full"}:
                # a mix of product and service lines, all product lines fully received
                result = "full"
            elif statuses == {"pending"}:
                result = "pending"
            else:
                # mix of full/pending/None => partial
                result = "partial"

            if move.receipt_status != result:
                move.receipt_status = result
