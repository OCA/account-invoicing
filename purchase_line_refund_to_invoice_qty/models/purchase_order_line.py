# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_refunded_not_invoiceable = fields.Float(
        compute="_compute_qty_refunded_not_invoiceable",
        string="Quantity Refunded Not Invoiceable",
        digits="Product Unit of Measure",
    )

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "invoice_lines.purchase_qty_to_reinvoice",
        "order_id.state",
        "qty_received",
    )
    def _compute_qty_invoiced(self):
        res = super()._compute_qty_invoiced()
        for line in self:
            qty_invoiced = line.qty_invoiced
            for invoice_line in line.invoice_lines:
                if (
                    invoice_line.move_id.state != "cancel"
                    and invoice_line.move_id.move_type == "in_refund"
                    and not invoice_line.purchase_qty_to_reinvoice
                ):
                    qty_invoiced += invoice_line.product_uom_id._compute_quantity(
                        invoice_line.quantity, line.product_uom
                    )

            line.qty_invoiced = qty_invoiced
            if line.order_id.state in ["purchase", "done"]:
                if line.product_id.purchase_method == "purchase":
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

        return res

    @api.depends(
        "product_uom_qty",
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "invoice_lines.purchase_qty_to_reinvoice",
    )
    def _compute_qty_refunded_not_invoiceable(self):
        for line in self:
            qty_ref_not_inv = 0.0
            for invoice_line in line.invoice_lines:
                if (
                    invoice_line.move_id.state != "cancel"
                    and invoice_line.move_id.move_type == "in_refund"
                    and not invoice_line.purchase_qty_to_reinvoice
                ):
                    qty_ref_not_inv += invoice_line.product_uom_id._compute_quantity(
                        invoice_line.quantity, line.product_uom
                    )
            line.qty_refunded_not_invoiceable = qty_ref_not_inv
