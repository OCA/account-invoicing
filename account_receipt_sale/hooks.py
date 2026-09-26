# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    # When installed on a DB with pre-existing out_receipt invoices linked
    # to sale order lines, recompute qty_invoiced and untaxed_amount_invoiced
    # so the receipts already in the system are rolled up into the totals.
    lines = env["sale.order.line"].search(
        [("invoice_lines.move_id.move_type", "=", "out_receipt")]
    )
    if lines:
        lines.invalidate_recordset(["qty_invoiced", "untaxed_amount_invoiced"])
        lines._compute_qty_invoiced()
        lines._compute_untaxed_amount_invoiced()
        lines.flush_recordset()
