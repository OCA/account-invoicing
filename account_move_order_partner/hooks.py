# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools.sql import column_exists


def pre_init_hook(cr):
    if not column_exists(cr, "account_move", "order_partner_id"):
        cr.execute(
            """
            ALTER TABLE account_move
                ADD COLUMN order_partner_id INTEGER
                REFERENCES res_partner(id)
                ON DELETE SET NULL;
            """
        )
    cr.execute(
        """
        WITH spc AS (
            SELECT
                am.id AS move_id,
                COUNT(DISTINCT sol.order_partner_id) AS cnt,
                MIN(sol.order_partner_id) AS single_partner_id
            FROM account_move am
            LEFT JOIN account_move_line aml
                   ON aml.move_id = am.id
            LEFT JOIN sale_order_line_invoice_rel rel
                   ON rel.invoice_line_id = aml.id
            LEFT JOIN sale_order_line sol
                   ON sol.id = rel.order_line_id
            WHERE am.move_type IN ('out_invoice', 'out_refund')
            GROUP BY am.id
        )
        UPDATE account_move am
        SET order_partner_id = CASE
            WHEN spc.cnt = 1 AND spc.single_partner_id IS NOT NULL
                THEN spc.single_partner_id
            ELSE am.partner_id
        END
        FROM spc
        WHERE am.id = spc.move_id
          AND am.move_type IN ('out_invoice', 'out_refund')
          AND am.order_partner_id IS NULL;
        """
    )
