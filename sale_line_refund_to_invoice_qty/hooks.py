from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """
    Recompute the `untaxed_amount_invoiced` field for sale.order.line records
    where `sale_qty_to_reinvoice` is False on their related account.move.lines.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    move_lines = env["account.move.line"].search(
        [("sale_qty_to_reinvoice", "=", False)]
    )
    sale_lines = move_lines.mapped("sale_line_ids")
    sale_lines._compute_untaxed_amount_invoiced()
