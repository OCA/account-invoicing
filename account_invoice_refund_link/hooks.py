# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def match_origin_lines(refund):
    """Try to match lines by product or by description."""
    invoice = refund.reversed_entry_id
    invoice_lines = invoice.invoice_line_ids
    for refund_line in refund.invoice_line_ids:
        for invoice_line in invoice_lines:
            match = (
                refund_line.product_id
                and refund_line.product_id == invoice_line.product_id
                or refund_line.name == invoice_line.name
            )
            if match:
                invoice_lines -= invoice_line
                refund_line.origin_line_id = invoice_line.id
                break
        if not invoice_lines:
            break


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Linking all refund invoices to its original invoices
    refunds = env["account.move"].search(
        [
            ("move_type", "in", ("out_refund", "in_refund")),
            ("reversed_entry_id", "!=", False),
        ]
    )
    for refund in refunds:
        match_origin_lines(refund)
