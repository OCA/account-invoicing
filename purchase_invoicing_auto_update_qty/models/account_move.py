# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    po_invoice_auto_update_qty = fields.Boolean(
        compute="_compute_po_invoice_auto_update_qty",
        string="Auto-update invoice quantities from PO",
        store=True,
        readonly=False,
        precompute=True,
    )

    @api.depends("company_id")
    def _compute_po_invoice_auto_update_qty(self):
        for move in self:
            po_invoice_auto_update_qty = move.company_id.po_invoice_auto_update_qty
            if move.po_invoice_auto_update_qty != po_invoice_auto_update_qty:
                move.po_invoice_auto_update_qty = po_invoice_auto_update_qty
