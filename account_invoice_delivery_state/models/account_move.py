# Copyright 2026 Allied Vision Technologies Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    has_storable_lines = fields.Boolean(
        compute="_compute_has_storable_lines",
        store=True,
        help="True when at least one invoice line contains a storable product.",
    )
    delivery_status = fields.Selection(
        selection=[
            ("pending", "Not Delivered"),
            ("partial", "Partially Delivered"),
            ("full", "Fully Delivered"),
        ],
        compute="_compute_delivery_status",
        store=True,
        index=True,
        copy=False,
        help=(
            "Delivery fulfillment state for customer invoices (out_invoice). "
            "False when the invoice has no storable products or no source sales order."
        ),
    )
    receipt_status = fields.Selection(
        selection=[
            ("pending", "Not Received"),
            ("partial", "Partially Received"),
            ("full", "Fully Received"),
        ],
        compute="_compute_receipt_status",
        store=True,
        index=True,
        copy=False,
        help=(
            "Receipt fulfillment state for vendor bills (in_invoice). "
            "False when the bill has no storable products or no source purchase order."
        ),
    )

    # ------------------------------------------------------------------
    # Depends helpers
    # ------------------------------------------------------------------

    @api.depends(
        "invoice_line_ids.product_id",
        "invoice_line_ids.product_id.is_storable",
    )
    def _compute_has_storable_lines(self):
        for move in self:
            move.has_storable_lines = any(
                line.product_id and line.product_id.is_storable
                for line in move.invoice_line_ids
            )

    # ------------------------------------------------------------------
    # Delivery status (customer invoices – out_invoice)
    # ------------------------------------------------------------------

    @api.depends(
        "has_storable_lines",
        "move_type",
        "state",
        "invoice_date",
        "date",
        "invoice_line_ids.product_id",
        "invoice_line_ids.quantity",
        "invoice_line_ids.product_uom_id",
        "invoice_line_ids.sale_line_ids.qty_delivered",
        "invoice_line_ids.sale_line_ids.product_uom_id",
        "invoice_line_ids.sale_line_ids.invoice_lines.quantity",
        "invoice_line_ids.sale_line_ids.invoice_lines.product_uom_id",
        "invoice_line_ids.sale_line_ids.invoice_lines.move_id.state",
        "invoice_line_ids.sale_line_ids.invoice_lines.move_id.invoice_date",
        "invoice_line_ids.sale_line_ids.invoice_lines.move_id.date",
    )
    def _compute_delivery_status(self):
        candidate_moves = self.filtered(
            lambda m: m.move_type == "out_invoice"
            and m.state != "cancel"
            and m.has_storable_lines
        )
        (self - candidate_moves).delivery_status = False

        if not candidate_moves:
            return

        candidate_lines = candidate_moves.invoice_line_ids.filtered(
            lambda line: line.display_type == "product"
            and line.product_id
            and line.product_id.is_storable
            and line.sale_line_ids
        )
        if not candidate_lines:
            candidate_moves.delivery_status = False
            return

        allocated_delivered = self._allocate_delivered_quantities_fifo(candidate_lines)

        for move in candidate_moves:
            storable_lines = move.invoice_line_ids.filtered(
                lambda line: line.display_type == "product"
                and line.product_id
                and line.product_id.is_storable
            )
            if not any(line.sale_line_ids for line in storable_lines):
                move.delivery_status = False
                continue

            total_invoiced_base = 0.0
            total_delivered_base = 0.0

            for line in storable_lines:
                base_uom = line.product_id.uom_id
                qty_base = line.product_uom_id._compute_quantity(
                    line.quantity, base_uom, round=False
                )
                total_invoiced_base += qty_base
                alloc_base = allocated_delivered.get(line.id, 0.0)
                total_delivered_base += min(alloc_base, qty_base)

            if total_invoiced_base <= 0:
                move.delivery_status = False
            elif float_is_zero(total_delivered_base, precision_digits=4):
                move.delivery_status = "pending"
            elif (
                float_compare(
                    total_delivered_base, total_invoiced_base, precision_digits=4
                )
                >= 0
            ):
                move.delivery_status = "full"
            else:
                move.delivery_status = "partial"

    def _allocate_delivered_quantities_fifo(self, candidate_lines):
        """Allocate delivered quantities from sale.order.line using FIFO.

        Multi-line and multi-order safe:
        - Prevents double-allocation across multiple order lines.
        - Preserves unrounded precision until final comparison.
        - Prioritizes invoices by (invoice_date or date, move_id.id, line.id).
        """
        all_sols = candidate_lines.sale_line_ids
        avail_delivered = {}
        for sol in all_sols:
            base_uom = sol.product_id.uom_id
            avail_delivered[sol.id] = sol.product_uom_id._compute_quantity(
                sol.qty_delivered, base_uom, round=False
            )

        all_sibling_lines = all_sols.invoice_lines.filtered(
            lambda line: line.display_type == "product"
            and line.move_id.move_type == "out_invoice"
            and line.move_id.state != "cancel"
            and line.sale_line_ids
        )

        sorted_lines = all_sibling_lines.sorted(
            key=lambda line: (
                line.move_id.invoice_date
                or line.move_id.date
                or fields.Date.context_today(line),
                line.move_id._origin.id or 0,
                line._origin.id or 0,
            )
        )

        allocated_qty = defaultdict(float)
        for line in sorted_lines:
            base_uom = line.product_id.uom_id
            needed_base = line.product_uom_id._compute_quantity(
                line.quantity, base_uom, round=False
            )
            for sol in line.sale_line_ids:
                if needed_base <= 0:
                    break
                available = avail_delivered.get(sol.id, 0.0)
                if available <= 0:
                    continue
                take = min(needed_base, available)
                allocated_qty[line.id] += take
                avail_delivered[sol.id] -= take
                needed_base -= take

        return allocated_qty

    # ------------------------------------------------------------------
    # Receipt status (vendor bills – in_invoice)
    # ------------------------------------------------------------------

    @api.depends(
        "has_storable_lines",
        "move_type",
        "state",
        "invoice_date",
        "date",
        "invoice_line_ids.product_id",
        "invoice_line_ids.quantity",
        "invoice_line_ids.product_uom_id",
        "invoice_line_ids.purchase_line_id.qty_received",
        "invoice_line_ids.purchase_line_id.product_uom_id",
        "invoice_line_ids.purchase_line_id.invoice_lines.quantity",
        "invoice_line_ids.purchase_line_id.invoice_lines.product_uom_id",
        "invoice_line_ids.purchase_line_id.invoice_lines.move_id.state",
        "invoice_line_ids.purchase_line_id.invoice_lines.move_id.invoice_date",
        "invoice_line_ids.purchase_line_id.invoice_lines.move_id.date",
    )
    def _compute_receipt_status(self):
        candidate_moves = self.filtered(
            lambda m: m.move_type == "in_invoice"
            and m.state != "cancel"
            and m.has_storable_lines
        )
        (self - candidate_moves).receipt_status = False

        if not candidate_moves:
            return

        candidate_lines = candidate_moves.invoice_line_ids.filtered(
            lambda line: line.display_type == "product"
            and line.product_id
            and line.product_id.is_storable
            and line.purchase_line_id
        )
        if not candidate_lines:
            candidate_moves.receipt_status = False
            return

        allocated_received = self._allocate_received_quantities_fifo(candidate_lines)

        for move in candidate_moves:
            storable_lines = move.invoice_line_ids.filtered(
                lambda line: line.display_type == "product"
                and line.product_id
                and line.product_id.is_storable
            )
            if not any(line.purchase_line_id for line in storable_lines):
                move.receipt_status = False
                continue

            total_invoiced_base = 0.0
            total_received_base = 0.0

            for line in storable_lines:
                base_uom = line.product_id.uom_id
                qty_base = line.product_uom_id._compute_quantity(
                    line.quantity, base_uom, round=False
                )
                total_invoiced_base += qty_base
                alloc_base = allocated_received.get(line.id, 0.0)
                total_received_base += min(alloc_base, qty_base)

            if total_invoiced_base <= 0:
                move.receipt_status = False
            elif float_is_zero(total_received_base, precision_digits=4):
                move.receipt_status = "pending"
            elif (
                float_compare(
                    total_received_base, total_invoiced_base, precision_digits=4
                )
                >= 0
            ):
                move.receipt_status = "full"
            else:
                move.receipt_status = "partial"

    def _allocate_received_quantities_fifo(self, candidate_lines):
        """Allocate received quantities from PO line to bill lines using FIFO."""
        all_pols = candidate_lines.purchase_line_id
        avail_received = {}
        for pol in all_pols:
            base_uom = pol.product_id.uom_id
            avail_received[pol.id] = pol.product_uom_id._compute_quantity(
                pol.qty_received, base_uom, round=False
            )

        all_sibling_lines = all_pols.invoice_lines.filtered(
            lambda line: line.display_type == "product"
            and line.move_id.move_type == "in_invoice"
            and line.move_id.state != "cancel"
            and line.purchase_line_id
        )

        sorted_lines = all_sibling_lines.sorted(
            key=lambda line: (
                line.move_id.invoice_date
                or line.move_id.date
                or fields.Date.context_today(line),
                line.move_id._origin.id or 0,
                line._origin.id or 0,
            )
        )

        allocated_qty = defaultdict(float)
        for line in sorted_lines:
            base_uom = line.product_id.uom_id
            needed_base = line.product_uom_id._compute_quantity(
                line.quantity, base_uom, round=False
            )
            pol = line.purchase_line_id
            if pol and needed_base > 0:
                available = avail_received.get(pol.id, 0.0)
                if available > 0:
                    take = min(needed_base, available)
                    allocated_qty[line.id] += take
                    avail_received[pol.id] -= take

        return allocated_qty
