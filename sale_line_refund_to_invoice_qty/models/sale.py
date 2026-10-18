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
        "invoice_lines.sale_qty_to_reinvoice",
    )
    def _get_invoice_qty(self):
        res = super()._get_invoice_qty()
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

    @api.depends("invoice_lines.sale_qty_to_reinvoice")
    def _compute_untaxed_amount_invoiced(self):
        """
        Revert effect of refunds in untaxed_amount_invoiced
        when `sale_qty_to_reinvoice` is not set.
        """
        res = super()._compute_untaxed_amount_invoiced()
        for line in self:
            amount_invoiced = line.untaxed_amount_invoiced
            for invoice_line in line.invoice_lines:
                if (
                    invoice_line.move_id.state == "posted"
                    and invoice_line.move_id.move_type == "out_refund"
                    and not invoice_line.sale_qty_to_reinvoice
                ):
                    invoice_date = (
                        invoice_line.move_id.invoice_date or fields.Date.today()
                    )
                    amount_invoiced += invoice_line.currency_id._convert(
                        invoice_line.price_subtotal,
                        line.currency_id,
                        line.company_id,
                        invoice_date,
                    )
            line.untaxed_amount_invoiced = amount_invoiced
        return res
