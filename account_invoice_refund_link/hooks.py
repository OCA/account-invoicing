# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def match_origin_lines(refund):
    """Try to match lines by product or by description."""
    invoice = refund.refund_invoice_id
    invoice_lines = invoice.invoice_line_ids
    for refund_line in refund.invoice_line_ids:
        for invoice_line in invoice_lines:
            match = (
                refund_line.product_id and
                refund_line.product_id == invoice_line.product_id or
                refund_line.name == invoice_line.name
            )
            if match:
                invoice_lines -= invoice_line
                refund_line.origin_line_ids = [(6, 0, invoice_line.ids)]
                break
        if not invoice_lines:
            break


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Linking all refund invoices to its original invoices
        refunds = env['account.invoice'].search([
            ('type', 'in', ('out_refund', 'in_refund')),
            ('refund_invoice_id', '!=', False),
        ])
        for refund in refunds:
            match_origin_lines(refund)
