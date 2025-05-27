# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Initializing last invoice and bill dates for partners.")
    cr.execute(
        """
        WITH RECURSIVE partner_tree AS (
            SELECT id, id AS root_id FROM res_partner
            UNION ALL
            SELECT child.id, partner_tree.root_id
            FROM res_partner AS child
            JOIN partner_tree ON child.parent_id = partner_tree.id
        )
        UPDATE res_partner p SET
            last_invoice_date = sub.max_inv_date,
            last_bill_date = sub.max_bill_date
        FROM (
            SELECT
                pt.root_id AS partner_id,
                MAX(
                    CASE WHEN am.move_type IN ('out_invoice', 'out_refund')
                    THEN am.invoice_date ELSE NULL END
                ) AS max_inv_date,
                MAX(
                    CASE WHEN am.move_type IN ('in_invoice', 'in_refund')
                    THEN am.invoice_date ELSE NULL END
                ) AS max_bill_date
            FROM partner_tree pt
            JOIN account_move am ON am.partner_id = pt.id
            WHERE am.state = 'posted' AND am.invoice_date IS NOT NULL
            GROUP BY pt.root_id
        ) sub
        WHERE p.id = sub.partner_id
    """
    )
