# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# Copyright 2022 Simone Rubino - TAKOBI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models

from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_refunded_not_invoiceable = fields.Float(
        compute="_compute_qty_refunded_not_invoiceable",
        string="Quantity Refunded Not Invoiceable",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    refund_invoice_line_ids = fields.Many2many(
        comodel_name='account.invoice.line',
        relation='refund_sale_invoice_lines_rel',
        string="Refund Lines linked to this Sale Order Line",
    )

    @api.depends(
        "refund_invoice_line_ids.invoice_id.state",
        "refund_invoice_line_ids.invoice_id.type",
        "refund_invoice_line_ids.sale_qty_to_reinvoice",
        "refund_invoice_line_ids.uom_id",
        "refund_invoice_line_ids.quantity",
        "product_uom",
    )
    def _get_invoice_qty(self):
        super()._get_invoice_qty()
        for line in self:
            qty_invoiced = line.qty_invoiced
            for invoice_line in line.refund_invoice_line_ids:
                if (
                    invoice_line.invoice_id.state != "cancel"
                    and invoice_line.invoice_id.type == "out_refund"
                    and invoice_line.sale_qty_to_reinvoice
                ):
                    qty_invoiced -= invoice_line.uom_id \
                        ._compute_quantity(
                            invoice_line.quantity, line.product_uom
                        )
            line.qty_invoiced = qty_invoiced

    @api.depends(
        "refund_invoice_line_ids.invoice_id.state",
        "refund_invoice_line_ids.invoice_id.type",
        "refund_invoice_line_ids.sale_qty_to_reinvoice",
        "refund_invoice_line_ids.uom_id",
        "refund_invoice_line_ids.quantity",
        "product_uom",
    )
    def _compute_qty_refunded_not_invoiceable(self):
        for line in self:
            qty_ref_not_inv = 0.0
            for invoice_line in line.refund_invoice_line_ids:
                if (
                    invoice_line.invoice_id.state != "cancel"
                    and invoice_line.invoice_id.type == "out_refund"
                    and not invoice_line.sale_qty_to_reinvoice
                ):
                    qty_ref_not_inv += invoice_line.uom_id \
                        ._compute_quantity(
                            invoice_line.quantity, line.product_uom
                        )
            line.qty_refunded_not_invoiceable = qty_ref_not_inv
