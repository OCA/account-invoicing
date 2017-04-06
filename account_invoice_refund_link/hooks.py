# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


def _invoice_match(env, invoice):
    inv_type = 'out_invoice' if invoice.type == 'out_refund' else 'in_invoice'
    return env['account.invoice'].search([
        ('type', '=', inv_type),
        ('number', '=ilike', invoice.origin),
    ])


def match_origin_lines(refund, invoice):
    """Try to match lines by product or by description."""
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
                invoice_line.origin_line_ids = [(6, 0, refund_line.ids)]
                break
        if not invoice_lines:
            break


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Linking all refund invoices to its original invoices
        refunds = env['account.invoice'].search([
            ('type', 'in', ('out_refund', 'in_refund')),
            ('origin_invoice_ids', '=', False),
        ])
        _logger.info("Linking %d refund invoices", len(refunds))
        for refund in refunds:
            original = _invoice_match(env, refund)
            if not original:  # pragma: no cover
                continue
            refund.write({
                'origin_invoice_ids': [(6, 0, original.ids)],
                'refund_reason': _('Auto'),
            })
            match_origin_lines(refund, original)
