# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_is_zero, float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        if self.purchase_id and self.journal_id and self.journal_id.avoid_zero_lines:
            if line.product_id.purchase_method == "purchase":
                qty = line.product_qty - line.qty_invoiced
            else:
                qty = line.qty_received - line.qty_invoiced
            if (
                float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding)
                <= 0
            ):
                qty = 0.0
            if float_is_zero(qty, precision_rounding=line.product_uom.rounding):
                return {}
        return super()._prepare_invoice_line_from_po_line(line)
