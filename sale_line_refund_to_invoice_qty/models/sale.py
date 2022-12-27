# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_refunded_not_invoiceable = fields.Float(
        compute="_compute_qty_refunded_not_invoiceable",
        string="Quantity Refunded Not Invoiceable",
        digits="Product Unit of Measure",
    )

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "untaxed_amount_to_invoice",
        "invoice_lines.sale_qty_to_reinvoice",
    )
    def _compute_qty_invoiced(self):
        res = super()._compute_qty_invoiced()
        # Revert effect of refunds in invoice_qty when `sale_qty_to_reinvoice`
        # is not set.
        for line in self:
            qty_invoiced = line.qty_invoiced
            for invoice_line in line.invoice_lines:
                if (
                    invoice_line.move_id.state != "cancel"
                    and invoice_line.move_id.move_type == "out_refund"
                    and not invoice_line.sale_qty_to_reinvoice
                ):
                    qty_invoiced += invoice_line.product_uom_id._compute_quantity(
                        invoice_line.quantity, line.product_uom
                    )
            line.qty_invoiced = qty_invoiced
        return res

    @api.depends(
        "product_uom_qty",
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "invoice_lines.sale_qty_to_reinvoice",
    )
    def _compute_qty_refunded_not_invoiceable(self):
        for line in self:
            qty_ref_not_inv = 0.0
            for invoice_line in line.invoice_lines:
                if (
                    invoice_line.move_id.state != "cancel"
                    and invoice_line.move_id.move_type == "out_refund"
                    and not invoice_line.sale_qty_to_reinvoice
                ):
                    qty_ref_not_inv += invoice_line.product_uom_id._compute_quantity(
                        invoice_line.quantity, line.product_uom
                    )
            line.qty_refunded_not_invoiceable = qty_ref_not_inv
