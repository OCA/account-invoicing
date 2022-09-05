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
        "qty_invoiced",
        "qty_delivered",
        "product_uom_qty",
        "order_id.state",
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "invoice_lines.sale_qty_to_reinvoice",
    )
    def _get_to_invoice_qty(self):
        super()._get_to_invoice_qty()
        for line in self:
            qty_to_invoice = line.qty_to_invoice
            for invoice_line in line.invoice_lines:
                if (
                    invoice_line.move_id.state != "cancel"
                    and invoice_line.move_id.type == "out_refund"
                    and not invoice_line.sale_qty_to_reinvoice
                ):
                    qty_to_invoice -= invoice_line.product_uom_id._compute_quantity(
                        invoice_line.quantity, line.product_uom
                    )
            line.qty_to_invoice = qty_to_invoice

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
                    and invoice_line.move_id.type == "out_refund"
                    and not invoice_line.sale_qty_to_reinvoice
                ):
                    qty_ref_not_inv += invoice_line.product_uom_id._compute_quantity(
                        invoice_line.quantity, line.product_uom
                    )
            line.qty_refunded_not_invoiceable = qty_ref_not_inv
