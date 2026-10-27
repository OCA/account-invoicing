# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.float_utils import float_is_zero


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _synch_invoice_line_quantity(self):
        changed = self.browse()
        for line in self:
            qty_to_invoice = line.qty_to_invoice
            if float_is_zero(
                qty_to_invoice, precision_rounding=line.product_id.uom_id.rounding
            ):
                continue
            draft_invoice_lines = line.invoice_lines.filtered(
                lambda l: l.move_id.state == "draft"
                and l.move_id.po_invoice_auto_update_qty
                and l.move_id.move_type == "in_invoice"
            )
            if draft_invoice_lines:
                draft_line = draft_invoice_lines[0]
                draft_line.quantity += qty_to_invoice
                changed |= line
        return changed

    def _write(self, vals):
        result = super()._write(vals)
        if "qty_to_invoice" in vals:
            changed = self._synch_invoice_line_quantity()
            if changed:
                self.env.add_to_compute(self._fields["qty_to_invoice"], changed)
                changed.invalidate_recordset(["qty_to_invoice"])
        return result
